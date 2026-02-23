import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from "@/router.js";
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
// 全局配置 axios 携带 Cookie
axios.defaults.withCredentials = true;
const app = createApp(App)
import axios from "axios";
axios.defaults.baseURL ='http://localhost:8080'
app.use(ElementPlus,{
    locale:zhCn
})
app.use(router)
app.mount('#app')

for(const [key,component]of Object.entries(ElementPlusIconsVue) ){
    app.component(key,component)
}