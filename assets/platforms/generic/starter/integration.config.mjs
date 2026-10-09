// 产品接进影片工程的方式（永远不要改产品仓库）。
// repoDir 默认取 plan.repo。把 '@'（或仓库自己的别名）指到它的源码；把框架运行时模块
// （next/image、next/navigation 之类）映射到 src/adapters/ 里的显示替身。
export default {
  repoDir: null,
  // aliases: {'@': '/abs/repo/src', 'next/image': new URL('./src/adapters/next-image.jsx', import.meta.url).pathname},
  aliases: {},
  // 这些裸 import 保持外部化，运行时从影片工程的 node_modules 里解析。
  external: [],
  loaders: {},
  define: {},
  // 额外的 esbuild 选项。例如产品开了 verbatimModuleSyntax，纯类型 import 会被保留，
  // 把服务端运行时拖进 bundle：
  //   esbuild: {tsconfigRaw: {compilerOptions: {verbatimModuleSyntax: false}}},
  esbuild: {},
};
