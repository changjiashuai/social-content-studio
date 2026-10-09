// plan.json 里每个镜头 id 对应一个视图组件和一个 builder。builder 收到主时间轴。
import {TitleView, ComponentView, buildTitle, buildComponent} from './sample.jsx';
export const SHOT_VIEWS = {intro: TitleView, component: ComponentView, close: TitleView};
export const SHOT_BUILDERS = {intro: buildTitle('intro'), component: buildComponent('component'), close: buildTitle('close')};
