# 内置字体

界面用到的三套字体已全部内置在此目录(woff2),离线可用,不再依赖任何 CDN。
`index.html` 通过 `fonts.css` 引用它们。打包时 `cooling_envelope.spec` 的
`datas=[('web','web')]` 会把整个 `web/`(含本目录)打进产物。

| 字体 | 文件 | 用途 | 许可 | 来源 |
|---|---|---|---|---|
| Fraunces(可变,正/斜) | `fraunces-normal.woff2` / `fraunces-italic.woff2` | 西文标题衬线 | SIL OFL 1.1 | google/fonts · undercasetype/Fraunces |
| IBM Plex Mono(400/500) | `ibm-plex-mono-400.woff2` / `ibm-plex-mono-500.woff2` | 等宽小标 | SIL OFL 1.1 | google/fonts · IBM |
| LXGW 落霞文楷(Regular) | `lxgw-wenkai-regular.woff2` | 中文正文 | SIL OFL 1.1 | lxgw/LxgwWenKai |

三套字体均以 **SIL Open Font License 1.1** 分发,完整许可文本见同目录:
`OFL-Fraunces.txt`、`OFL-IBMPlexMono.txt`、`OFL-LXGWWenKai.txt`。

> woff2 由各自上游的 TTF 转换而来(`fontTools` + `brotli`),内容未做子集化,
> 中文为全字符覆盖,因此 `lxgw-wenkai-regular.woff2` 约 8MB。
