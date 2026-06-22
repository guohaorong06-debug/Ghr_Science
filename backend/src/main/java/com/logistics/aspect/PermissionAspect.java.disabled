package com.logistics.aspect;

import com.logistics.annotation.RequirePermission;
import com.logistics.service.PermissionService;
import com.logistics.utils.JwtUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import javax.servlet.http.HttpServletRequest;
import java.lang.reflect.Method;

/**
 * 权限校验切面
 *
 * 拦截所有标注了@RequirePermission的方法，进行权限校验
 */
@Slf4j
@Aspect
@Component
@RequiredArgsConstructor
public class PermissionAspect {

    private final PermissionService permissionService;
    private final JwtUtil jwtUtil;

    @Around("@annotation(com.logistics.annotation.RequirePermission)")
    public Object checkPermission(ProceedingJoinPoint joinPoint) throws Throwable {
        // 获取方法签名
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        Method method = signature.getMethod();

        // 获取注解
        RequirePermission annotation = method.getAnnotation(RequirePermission.class);
        String[] requiredPermissions = annotation.value();
        RequirePermission.Logical logical = annotation.logical();

        // 获取当前请求
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        if (attributes == null) {
            throw new RuntimeException("无法获取请求上下文");
        }

        HttpServletRequest request = attributes.getRequest();

        // 从请求头获取Token
        String token = request.getHeader("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            throw new RuntimeException("未登录或Token无效");
        }

        token = token.substring(7);

        // 解析Token获取用户名
        String username = jwtUtil.getUsernameFromToken(token);
        if (username == null) {
            throw new RuntimeException("Token无效");
        }

        // 如果是游客，直接拒绝（游客只能访问公开接口）
        if (username.startsWith("guest_")) {
            throw new RuntimeException("游客无权限访问此资源");
        }

        // 获取用户ID（需要从数据库查询，这里简化处理）
        // TODO: 从UserService获取userId
        Long userId = getUserIdByUsername(username);

        // 校验权限
        boolean hasPermission = false;
        if (logical == RequirePermission.Logical.AND) {
            // 必须拥有所有权限
            hasPermission = permissionService.hasAllPermissions(userId, requiredPermissions);
        } else {
            // 只需拥有其中一个权限
            hasPermission = permissionService.hasAnyPermission(userId, requiredPermissions);
        }

        if (!hasPermission) {
            log.warn("权限校验失败: userId={}, method={}, requiredPermissions={}",
                    userId, method.getName(), String.join(",", requiredPermissions));
            throw new RuntimeException("权限不足");
        }

        // 权限校验通过，执行目标方法
        return joinPoint.proceed();
    }

    /**
     * 根据用户名获取用户ID
     * TODO: 实际应该调用UserService
     */
    private Long getUserIdByUsername(String username) {
        // 临时实现，实际应该从数据库查询
        if ("admin".equals(username)) {
            return 1L;
        }
        return 0L;
    }
}
