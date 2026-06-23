import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { public: true },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue'),
        },
        {
          path: 'site',
          name: 'SiteManage',
          component: () => import('@/views/SiteManage.vue'),
        },
        {
          path: 'data-import',
          name: 'DataImport',
          component: () => import('@/views/DataImport.vue'),
        },
        {
          path: 'forecast',
          name: 'Forecast',
          component: () => import('@/views/Forecast.vue'),
        },
        {
          path: 'model',
          name: 'ModelManage',
          component: () => import('@/views/ModelManage.vue'),
        },
        {
          path: 'admin/users',
          name: 'UserManagement',
          component: () => import('@/views/admin/UserManagement.vue'),
          meta: { requiresAuth: true, permission: 'admin:user:view' },
        },
        {
          path: 'admin/roles',
          name: 'RoleManagement',
          component: () => import('@/views/admin/RoleManagement.vue'),
          meta: { requiresAuth: true, permission: 'admin:role:view' },
        },
        {
          path: 'admin/permissions',
          name: 'PermissionManagement',
          component: () => import('@/views/admin/PermissionManagement.vue'),
          meta: { requiresAuth: true, permission: 'admin:role:view' },
        },
      ],
    },
  ],
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const isPublic = to.meta.public

  // 未登录，跳转到登录页
  if (!isPublic && !userStore.token) {
    next('/login')
    return
  }

  // 已登录访问登录页，重定向到首页
  if (to.path === '/login' && userStore.token) {
    next('/')
    return
  }

  // 检查权限
  if (to.meta.permission && userStore.token) {
    const requiredPermission = to.meta.permission as string

    // 如果用户信息未加载，先加载
    if (!userStore.userInfo) {
      try {
        await userStore.fetchUserInfo()
      } catch (error) {
        console.error('获取用户信息失败:', error)
        userStore.logout()
        next('/login')
        return
      }
    }

    // 检查是否有权限
    if (!userStore.hasPermission(requiredPermission)) {
      console.warn(`无权限访问: ${to.path}, 需要权限: ${requiredPermission}`)
      next('/')
      return
    }
  }

  next()
})

export default router
