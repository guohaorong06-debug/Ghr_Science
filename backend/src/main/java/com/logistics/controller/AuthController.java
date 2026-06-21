package com.logistics.controller;

import com.logistics.entity.SysUser;
import com.logistics.service.SysUserService;
import com.logistics.utils.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.constraints.NotBlank;
import java.util.Map;

/**
 * 认证控制器
 */
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Validated
@Tag(name = "认证管理")
public class AuthController {

    private final SysUserService userService;

    @PostMapping("/login")
    @Operation(summary = "用户登录")
    public Result<Map<String, Object>> login(@RequestBody LoginRequest req) {
        return Result.ok(userService.login(req.getUsername(), req.getPassword()));
    }

    @PostMapping("/register")
    @Operation(summary = "用户注册")
    public Result<Void> register(@RequestBody RegisterRequest req) {
        SysUser user = new SysUser();
        user.setUsername(req.getUsername());
        user.setPassword(req.getPassword());
        user.setRealName(req.getRealName());
        user.setEmail(req.getEmail());
        user.setPhone(req.getPhone());
        userService.register(user);
        return Result.ok();
    }

    @GetMapping("/info")
    @Operation(summary = "获取当前用户信息")
    public Result<Map<String, Object>> getUserInfo(Authentication auth) {
        return Result.ok(userService.getUserInfo(auth.getName()));
    }

    @Data
    static class LoginRequest {
        @NotBlank(message = "用户名不能为空")
        private String username;
        @NotBlank(message = "密码不能为空")
        private String password;
    }

    @Data
    static class RegisterRequest {
        @NotBlank(message = "用户名不能为空")
        private String username;
        @NotBlank(message = "密码不能为空")
        private String password;
        private String realName;
        private String email;
        private String phone;
    }
}
