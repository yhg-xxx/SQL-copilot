 import {createRouter, createWebHashHistory} from "vue-router";
import Auth from "./components/Auth.vue";

const router = createRouter({
        history: createWebHashHistory(import.meta.env.BASE_URL),
        routes: [
            {
                path: "/",
                name: "multi-agent",
                component: () => import("./views/MultiAgentView.vue"),
                meta: { requiresAuth: true }
            },
            {
                path: "/datasource",
                name: "datasource",
                component: () => import("./views/DatasourceView.vue"),
                meta: { requiresAuth: true }
            },
            {
                path: "/database/:id",
                name: "database",
                component: () => import("./views/DatabaseView.vue"),
                meta: { requiresAuth: true }
            },
            {
                path: "/auth",
                name: "auth",
                component: Auth
            },
            {
                path: "/login",
                redirect: "/auth"
            },
            {
                path: "/register",
                redirect: "/auth"
            }
        ]

    }
)

// 路由守卫
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token');
    if (to.meta.requiresAuth && !token) {
        next('/auth');
    } else {
        next();
    }
});

export default router;