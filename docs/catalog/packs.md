# Packs Catalog

> This file is generated. Run `npm run build`.

| Name | Type | Version | Maturity | Categories | Members | Description |
| --- | --- | --- | --- | --- | --- | --- |
| [agentic-issue-delivery](../../packs/agentic-issue-delivery/README.md) | role-pack | 0.15.1 | experimental | workflow, coding, review | 13 skills, 6 agents, 2 hooks | Workflow pack for turning design-stage work into implementation-ready issues, then executing those issues through subagent-driven review and delivery gates. |
| [codebase-stewardship](../../packs/codebase-stewardship/README.md) | role-pack | 0.6.1 | experimental | coding, refactoring, review | 8 skills, 1 agents, 1 hooks | 周期性/按需的代码健康治理：深化模块、治乱删冗、定架构方向，共用 grill 对抗式对话与 openspec/glossary.md + docs/adr/ 领域沉淀。区别于 agentic-issue-delivery 的一次性 issue 交付流水线。 |
| [product-manager](../../packs/product-manager/README.md) | role-pack | 0.3.1 | experimental | business, productivity, research | 8 skills, 3 agents, 0 hooks | Product strategy, requirements, and research workflow pack. |
| [research-engineering](../../packs/research-engineering/README.md) | role-pack | 0.2.0 | experimental | research, design, workflow | 16 skills, 4 agents, 0 hooks | Research control-plane pack for turning phenomena, capability gaps, scientific ideas, model-process changes, data/method needs, and operational questions into governed research artifacts, reviewed evidence, human decisions, and optional engineering handoffs without constraining work to a closed task taxonomy. |
| [stellarlink](../../packs/stellarlink/README.md) | role-pack | 0.2.1 | experimental | coding, testing, workflow, security, design | 10 skills, 0 agents, 0 hooks | 从 stellarlink-skills 吸收的工程方法论组合：证据驱动交付（tdd/vdd/implement）、代码库级迁移（code-migration）、架构设计与 spec 化（architecture-design/to-spec）、视觉设计工程（visual-design）、仓库就绪控制面（eng-init）、可度量工件进化（self-evolution）与逆向工程路由（reverse-skill）。除 tdd/vdd（被其他 skill 运行中调用，保持模型可调）外全部手动调用。 |
