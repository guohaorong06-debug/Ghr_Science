<template>
  <div class="dashboard">
    <h1>决策仪表盘</h1>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <template #header>全网预测包裹量</template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <template #header>预警网点数</template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <template #header>活跃模型版本</template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <template #header>数据更新时间</template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top: 20px;">
      <template #header>功能模块进度</template>
      <p>✅ 用户认证 - 已完成</p>
      <p>✅ 网点管理 - 已完成</p>
      <p>✅ 数据导入 - 已完成</p>
      <p>✅ 预测服务 - 已完成（占位模型）</p>
      <p>✅ 预警决策 - 已完成</p>
      <p>✅ 模型管理 - 已完成（上传/激活/删除）</p>
      <p>⏳ PWA优化 - 待开发（阶段5）</p>
      <p>⏳ 科研代码 - 待开发（阶段6）</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.dashboard {
  h1 {
    margin-bottom: 20px;
  }

  .stat-value {
    font-size: 32px;
    font-weight: bold;
    text-align: center;
    color: #409eff;
  }
}
</style>
