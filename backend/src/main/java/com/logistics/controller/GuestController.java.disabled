package com.logistics.controller;

import com.logistics.service.GuestService;
import com.logistics.utils.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.Map;

/**
 * 游客访问控制器
 */
@RestController
@RequestMapping("/api/auth/guest")
@RequiredArgsConstructor
@Tag(name = "游客访问")
public class GuestController {

    private final GuestService guestService;

    @PostMapping("/login")
    @Operation(summary = "游客登录（临时访问）")
    public Result<Map<String, Object>> guestLogin(HttpServletRequest request) {
        try {
            Map<String, Object> result = guestService.createGuestSession(request);
            return Result.ok(result);
        } catch (Exception e) {
            return Result.error("游客登录失败：" + e.getMessage());
        }
    }

    @GetMapping("/info")
    @Operation(summary = "获取游客信息")
    public Result<Map<String, Object>> guestInfo(@RequestHeader("Authorization") String token) {
        // TODO: 解析Token，返回游客信息
        return Result.ok(Map.of(
                "type", "GUEST",
                "expiresIn", 7200,
                "permissions", new String[]{
                        "site:list",
                        "site:view",
                        "data:list",
                        "forecast:list"
                }
        ));
    }

    @PostMapping("/refresh")
    @Operation(summary = "刷新游客会话")
    public Result<String> refreshSession(@RequestParam String guestId) {
        try {
            guestService.refreshGuestSession(guestId);
            return Result.ok("会话已刷新");
        } catch (Exception e) {
            return Result.error("刷新失败：" + e.getMessage());
        }
    }
}
