package com.logistics.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 权限校验注解
 *
 * 用法：
 * @RequirePermission("system:user:add")
 * @RequirePermission(value = "site:delete", logical = Logical.AND)
 * @RequirePermission(value = {"site:add", "site:edit"}, logical = Logical.OR)
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RequirePermission {

    /**
     * 权限编码（单个或多个）
     */
    String[] value() default {};

    /**
     * 逻辑运算符（多个权限时使用）
     */
    Logical logical() default Logical.AND;

    /**
     * 逻辑运算符枚举
     */
    enum Logical {
        /**
         * 与运算（必须拥有所有权限）
         */
        AND,

        /**
         * 或运算（只需拥有其中一个权限）
         */
        OR
    }
}
