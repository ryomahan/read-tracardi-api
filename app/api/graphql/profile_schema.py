import typing
import strawberry
from strawberry.types import Info

from app.api.graphql.utils.casters import cast
from tracardi import domain
from tracardi.service.storage.driver.elastic import event as event_db
from tracardi.service.storage.driver.elastic import profile as profile_db
from app.api.graphql.interfaces import Entity
from app.api.graphql.scalars.json_scalar import JSONScalar
from tracardi.service.storage.elastic_storage import ElasticFiledSort


@strawberry.type
class EventMeta:
    time: str


@strawberry.type
class ProfileVisit:
    last: typing.Optional[str]
    current: typing.Optional[str]


@strawberry.type
class ProfileMeta:
    time: str
    visit: ProfileVisit
    merged_with: typing.Optional[str]


@strawberry.type
class ProfilePII:
    name: typing.Optional[str]
    surname: typing.Optional[str]
    birth_date: typing.Optional[str]
    marital_status: typing.Optional[str]
    email: typing.Optional[str]
    telephone: typing.Optional[str]
    twitter: typing.Optional[str]
    facebook: typing.Optional[str]
    whatsapp: typing.Optional[str]
    other: typing.Optional[JSONScalar]


@strawberry.type
class ProfileTraits:
    public: JSONScalar
    private: JSONScalar


@strawberry.type
class ProfileStats:
    visits: int
    views: int
    counters: JSONScalar


@strawberry.type
class Event(Entity):
    metadata: EventMeta
    type: str
    properties: typing.Optional[JSONScalar]

    source: Entity
    session: typing.Optional[JSONScalar]
    context: typing.Optional[JSONScalar]


@strawberry.type
class EventAggregationsBuckets:

    def __init__(self, id):
        self.id = id

    @strawberry.field
    async def by_time(self) -> 'JSONScalar':
        bucket_name = 'by_time'
        aggregated_events = await event_db.heatmap_by_profile(self.id, bucket_name)
        bucket, items = next(aggregated_events.iterate(bucket_name))  # There is only one key
        return items

    @strawberry.field
    async def by_type(self) -> 'JSONScalar':
        bucket_name = 'by_type'
        aggregated_events = await event_db.aggregate_profile_events_by_type(self.id, bucket_name)
        bucket, items = next(aggregated_events.iterate(bucket_name))  # There is only one key
        return items


@strawberry.type
class EventAggregations:
    aggregations: EventAggregationsBuckets


@strawberry.type
class Profile(Entity):
    metadata: ProfileMeta
    traits: ProfileTraits
    pii: ProfilePII
    stats: ProfileStats
    segments: typing.List[str]
    consents: JSONScalar
    active: bool
    event: EventAggregations

    @strawberry.field
    async def events(self, info: Info, type: typing.Optional[str] = None, limit: int = 20) -> typing.List[Event]:
        # print(info)
        # fields = info.selected_fields
        # print(fields[0].selections)
        key_value_pais = [
            ("profile.id", self.id)
        ]

        if type:
            key_value_pais.append(
                ("type", type)
            )

        sort_by = [
            ElasticFiledSort("metadata.time.insert", "DESC", 'strict_date_optional_time_nanos')
        ]

        events = await event_db.load_event_by_values(key_value_pais, sort_by, limit=limit)
        return [
            # todo add request data to event
            Event(
                id=event.id,
                metadata=EventMeta(time=original_event['metadata']['time']['insert']),
                type=event.type,
                properties=event.properties,
                source=Entity(id=event.source.id),
                session=event.session.dict(),
                context=event.context,
                config=event.config
            ) for event, original_event in cast(events, domain.event.Event, return_original=True)
        ]


@strawberry.type
class ProfileQuery:
    @strawberry.field
    async def profile(self, info: Info, id: strawberry.ID) -> Profile:
        record = await profile_db.load_by_id(id)
        if record is None:
            raise ValueError("There is no profile {}".format(id))
        profile = record.to_entity(domain.profile.Profile)

        return Profile(
            id=profile.id,
            metadata=ProfileMeta(time=profile.metadata.time.insert,
                                 visit=ProfileVisit(
                                     last=profile.metadata.time.visit.last,
                                     current=profile.metadata.time.visit.current)
                                 ),
            stats=ProfileStats(visits=profile.stats.visits, views=profile.stats.views, counters=profile.stats.counters),
            traits=ProfileTraits(**profile.traits.dict()),
            pii=ProfilePII(**profile.pii.dict()),
            segments=profile.segments,
            consents=profile.consents,
            active=profile.active,
            event=EventAggregations(aggregations=EventAggregationsBuckets(profile.id))
        )
