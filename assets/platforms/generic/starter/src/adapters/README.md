框架运行时模块的显示适配层（这里是 Next.js）。只有上镜组件真的 import 了它们，才在
integration.config.mjs 里 alias 过来。这些替身全是静态的：片子从不导航、不做图片优化、
不懒加载面板。换别的框架就按组件实际需要写等价物（router hooks、i18n loader、IPC 桥）。
