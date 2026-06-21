# Issue #30: 实现改动清单

- [ ] Task 1: 盘点并固化边界术语
  - [ ] 识别当前仓库中哪些文档在表达 `TGS Core`、`GitHub-backed TGS`、仓库级 operating rule、运行产物目录
  - [ ] 形成“当前表述 vs 目标表述”的差异清单
  - [ ] 明确哪些术语需要在本次变更中收紧，哪些术语留到后续 Issue 处理

- [ ] Task 2: 定义四层职责边界
  - [ ] 定义 `TGS Core` 的职责与不应承载的内容
  - [ ] 定义 `TGS Profile` 的职责与 GitHub-backed profile 的仓库定位
  - [ ] 定义 `TGS Adapter` 的职责与对装配器层的约束
  - [ ] 定义 `TGS Package` 的职责与为何不在本次变更中细化其格式

- [ ] Task 3: 明确目录与产物语义
  - [ ] 明确 `tgs/` 作为 source-of-truth 的角色
  - [ ] 明确 `.tgs/` 作为安装或渲染后运行产物的角色
  - [ ] 写清为什么 `.tgs/` 不能直接等同于未来的分发包

- [ ] Task 4: 对齐仓库级文档入口表述
  - [ ] 更新 `tgs/README.md`，让其引用边界定义而不是重复承载仓库运行语义
  - [ ] 更新 `tgs/operating-spec.md`，把 GitHub-backed TGS 收紧表述为 operating profile
  - [ ] 必要时更新 `tgs/instructions.md` 或 `.agent/rules/issue-driven.md` 的导航与 handoff 文案

- [ ] Task 5: 验证边界拆分未越权到后续 Issue
  - [ ] 验证本次变更未提前实现 profile 抽离目录
  - [ ] 验证本次变更未提前改造 assembler 的硬编码路径
  - [ ] 验证本次变更未提前定义 package manifest 或安装流程
  - [ ] 运行相关文档检查或测试，确保入口导航仍然成立

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 2
- Task 4 depends on Task 3
- Task 5 depends on Task 4
