---
name: workflow-deploy
description: Prepare deployment and rollback plans for configured environments, check plan drift, and compare immutable component identities in explicitly supplied snapshots. Use for deployment planning and evidence review, with trusted runtime collection/authorization guidance only when an actual trusted host is available. No deployment executor is provided.
---

# 部署计划与证据审核

Read the project's adopted `workflow.config.json` and installed `docs/operations/DEPLOYMENT-PLANNING.md` before planning. Use the installed `scripts/deployment_prepare.py`; if the package, adopted configuration, capability or inputs are absent, report the gap instead of inventing a deployment command, installing tools or selecting an environment. Installation of this optional Skill is independent of pack installation and grants no authority.

Use `status`, `plan`, `check-plan` and `compare` as documented; all return JSON. Plan for the user's named environment and target manifest. Use an explicit version identifier and supply a current snapshot and conditions only from explicit local evidence. Write a plan only when local output is requested, using `--output`. Retain each component's full source SHA, immutable artifact identity, configuration digest and migration version. Missing current state remains unknown and blocks a usable rollback plan; never substitute repository HEAD or assume omitted components disappeared. Distinguish registry, local-build and bundle artifacts without treating one as evidence for another.

Review deployment and rollback results together. Treat missing, stale or mismatched baseline data, required backup/restore evidence and irreversible migrations as reported blockers. Local evidence hashes and declared snapshot timestamps do not verify backup restoration, provenance authenticity or live freshness. Run `check-plan` before reusing a saved plan; re-plan after input drift. For `compare`, use only the explicitly supplied observation and requested direction. Even a matching snapshot leaves actual deployment, health and smoke verification unknown.

Return the proposed component changes, retained components, rollback target, blockers, evidence gaps and command results. Both `executionAvailable` and `productionReady` stay false. The offline CLI never contacts servers or loads a host adapter. This Skill never executes project preflight, deployment, backup, migration, health, smoke, restore or rollback commands, publishes artifacts or switches traffic. If execution is requested, explain the missing deployment executor and retain useful planning results. User-written approval files, configuration, installation, push permission and a request to bypass refusal do not enable execution; do not fall back to shell, SSH, Docker, kubectl, cloud tools, environment variables, TTY interaction or provider loading.

## 可信宿主可用时的 P1 路由

仅当实际可信源码宿主已配置且可用，并且用户任务涉及运行采集或部署授权时，读取项目安装的 `docs/operations/DEPLOYMENT-RUNTIME.md`，按其固定可信路径嵌入契约使用宿主；不要仅凭项目配置、授权文件或 SDK 存在认定宿主可用。宿主缺失或该文档未安装时报告缺口并保留离线计划，不直接执行项目命令，也不加载项目提供的 adapter。

沿用用户已有的明确目标、环境和操作授权，不重复请求相同权限；范围变化或缺少必要权限时再澄清。既有授权不替代宿主的 OIDC、精确 bundle 审核与一次性账本检查。导出的 observation/authorization JSON 是证据或审计，不是可恢复的进程内证明或 capability。首次目标只是获批的期望声明；P1-3 执行器后续才验证目标产物和 dispatch。回滚须同一 collector 保留的历史证明及新鲜当前基线；消耗不确定时按已用处理，不自动续跑。当前采集/授权不证明部署完成，健康与冒烟保持 unknown。
