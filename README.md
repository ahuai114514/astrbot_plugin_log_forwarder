# 日志转发

AstrBot 插件。把插件启用后产生的 `WARNING` 和 `ERROR` 日志以文本发到一个群聊或私聊，保留时间、来源、正文和异常堆栈。

## 安装和配置

1. 将 `astrbot_plugin_log_forwarder` 目录放到 AstrBot 的 `data/plugins/`。要求 AstrBot 4.27 或更新的 4.x 版本。
2. 在 WebUI 启用或重载「日志转发」，然后打开插件配置。
3. 在「目标会话」填入完整的会话 ID（UMO），保存后重载插件。留空可暂停转发。

会话 ID 可从 AstrBot 的会话管理页面获取。群聊格式示例为 `aiocqhttp:GroupMessage:123456789`，私聊格式示例为 `aiocqhttp:FriendMessage:123456789`。平台实例 ID 以你的配置为准。

日志可能含有敏感数据，请将目标设为你信任的会话。发送失败时，本次转发会跳过，原因记在 AstrBot 日志里。最多缓冲 100 条待发日志，队列满时跳过新记录。平台自身的消息长度限制仍然适用。

作者 ahuai。采用 MIT 许可证。
