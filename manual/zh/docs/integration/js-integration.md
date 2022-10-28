# 通过给网页注入 JS 锚点进行信息整合

## Connecting and configuring the script 

你可以通过给任何网页注入 Tracardi 给出的特定 JavaScript 代码片段让相应网页和 Tracardi 建立关联。

如果需要使用这种方式，你需要将下面的代码注入到页面的 header 标签中。 

```html
    <script>
        const options = {
            tracker: {
                url: {
                    script: 'http://192.168.1.103:8686/tracker',
                    api: 'http://192.168.1.103:8686'
                },
                source: {
                    id: "<your-resource-id-HERE>"
                }
            }
        }

        !function(e){"object"==typeof exports&&"undefine...
    </script>
```

如果你不加修改直接将上面的代码粘贴到你的页面上 Tracardi 会返回类似下面这样的响应：

```
Headers:
Status: 401 Unauthorized

Body:
{"detail": "Access denied. Invalid source."}
```

这是因为给出的示例代码 option.source.id 部分并没有定义有效的  source id。你可以通过在 Tracardi 控制台创建资源并用给出的资源 id 替换示例代码中的 `<your-resource-id-HERE>`，例如：

```html
    <script>
        const options = {
            tracker: {
                url: {
                    script: 'http://192.168.1.103:8686/tracker',
                    api: 'http://192.168.1.103:8686'
                },
                source: {
                    id: "ee2db027-46cf-4034-a759-79f1c930f80d"
                }
            }
        }

        !function(e){"object"==typeof exports&&"undefined"!=ty...
    </script>
```

同样需要注意：你需要在实际使用过程中将 `192.168.1.103:8686` 替换成你实际运行的 Tracardi API 服务的地址和端口。

## Sending events

在做好上面这些准备后就可以尝试发送事件数据给 Tracardi 了。

你可以将你想要发送的事件数据内容写在一个单独的 JavaScript 脚本中，例如：

```javascript
window.response.context.profile = true;
window.tracker.track("purchase-order", {"product": "Sun glasses - Badoo", "price": 13.45})
window.tracker.track("interest", {"Eletronics": ["Mobile phones", "Accessories"]})
window.tracker.track("page-view",{});
```

事件数据至少由一个事件类型组成，事件类型可以是描述用户具体行为的任意字符串。

在示例中我们定义了三个事件类型："purchase-order", "interest", "page-view"。

### 事件数据和属性

每个事件都可以有额外的数据用来描述事件的细节。

例如我们定义了一个 interest 事件并且给他附加了额外的数据：`{"Eletronics": ["Mobile phones", "Accessories"]}`

你之前埋下的 JavaScript 代码片段会收集所有事件数据并且通过请求将事件数据发送给 Tracardi tracker endpoint。

TODO：这是什么原理
所有事件数据会在网站页面加载完成后发送。

## 将事件触发锚点绑定到页面元素上

你也可以将事件触发锚点绑定在页面的元素上。在此之前，你需要确定页面已经加载完成并且页面上的元素是可访问的。

你可以给示例代码片段中的 options 添加如下内容：

```javascript
listeners: {
    onContextReady: ({helpers, context}) => {
      // Code that binds events.
    }
}
```

完整的配置信息如下所示：

```html
<script>
        const options = {
            listeners: {
                onContextReady: ({helpers, context}) => {
                    // Code that binds events.
                },
            tracker: {
                url: {
                    script: 'http://192.168.1.103:8686/tracker',
                    api: 'http://192.168.1.103:8686'
                },
                source: {
                    id: "ee2db027-46cf-4034-a759-79f1c930f80d"
                }
            }
        }

        !function(e){"object"==typeof exports&&"undefined"!=ty...
</script>
```

然后你可以写一段 JavaScript 代码将 Tracardi 事件与页面上指定按钮的 onClick 事件进行绑定，如下所示：

```javascript
onContextReady: ({helpers, context}) => {
    const btn0 = document.querySelector('#button')

    helpers.onClick(btn0, async ()=> {
        const response = await helpers.track("page-view", {"page": "hello"});

        if(response) {
            const responseToCustomEvent = document.getElementById('response-to-custom-event');
            responseToCustomEvent.innerText = JSON.stringify(response.data, null, " ");
            responseToCustomEvent.style.display = "block"
        }
    });
}
```

示例中下面这段代码的作用是从网页中查找 `id=button` 的元素。

```javascript
const btn0 = document.querySelector('#button')
```

示例中下面这段代码的作用是利用 helpers 将指定页面元素的 onClink 事件绑定指定方法。

```javascript
helpers.onClick(btn0, async ()=> {
    const response = await helpers.track("page-view", {"page": "hello"});

    if(response) {
        const responseToCustomEvent = document.getElementById('response-to-custom-event');
        responseToCustomEvent.innerText = JSON.stringify(response.data, null, " ");
        responseToCustomEvent.style.display = "block"
    }
});
```

示例中下面这段代码的作用是利用 helpers 将事件发送给 Tracardi。

```javascript
const response = await helpers.track("page-view", {"page": "hello"});
```

在获取到 Tracardi 响应候会从 JSON response 产生一个字符串并将其作为 `id=response-to-custom-event` 网页元素的 innerText。

## 总结

到目前为止完整的示例代码如下所示：
 
```html
 <script>
         const options = {
             listeners: {
                 onContextReady: ({helpers, context}) => {
                     const btn0 = document.querySelector('#button')
                 
                     helpers.onClick(btn0, async ()=> {
                         const response = await helpers.track("page-view", {"page": "hello"});
                 
                         if(response) {
                             const responseToCustomEvent = document.getElementById('response-to-custom-event');
                             responseToCustomEvent.innerText = JSON.stringify(response.data, null, " ");
                             responseToCustomEvent.style.display = "block"
                         }
                     });
                 },
             tracker: {
                 url: {
                     script: 'http://192.168.1.103:8686/tracker',
                     api: 'http://192.168.1.103:8686'
                 },
                 source: {
                     id: "ee2db027-46cf-4034-a759-79f1c930f80d"
                 }
             }
         }
 
         !function(e){"object"==typeof exports&&"undefined"!=ty...
 </script>
 ```

## Tracardi helpers

你可能注意到了，我们使用 helpers 完成了网页事件和 Tracardi 事件的绑定。在示例中我们使用 onClick 方法捕获到了网页元素的点击事件，你也许需要捕获更多的网页事件，可以使用 helpers 提供的 addEventListener 方法：

```javascript
const btn0 = document.querySelector('#button')                 
helpers.addListener(btn0, 'mouseover', async ()=> {
    // Code
});
```

Helpers 也内置了一个 track 方法，方便你再任何时刻向 Tracardi 发送自定义的事件。