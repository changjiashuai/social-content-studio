// 懒加载的产品面板不属于任何镜头。
export default function dynamic() {
  return function DynamicPlaceholder() { return null; };
}
