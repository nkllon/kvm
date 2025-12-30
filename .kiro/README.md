# Spec-Driven Development for NKLLON

This directory contains specifications following the cc-sdd (Spec-Driven Development) framework.

## Quick Start

To adopt cc-sdd for this project:

```bash
# Install cc-sdd
npx cc-sdd@latest --claude --lang en

# Initialize spec for the existing system
/kiro:spec-init Hardware topology validation system for KVM setups using semantic web technologies

# Generate requirements document
/kiro:spec-requirements kvm-topology-en

# Generate design document
/kiro:spec-design kvm-topology-en -y

# Generate task breakdown
/kiro:spec-tasks kvm-topology-en -y
```

## Directory Structure

Once initialized, this directory will contain:

```
.kiro/
├── specs/
│   └── kvm-topology-en/
│       ├── requirements.md    # Formal EARS-format requirements
│       ├── design.md          # Architecture and design decisions
│       └── tasks.md           # Implementation task breakdown
└── README.md                  # This file
```

## Workflow

### 1. Requirements Phase
- Define functional requirements (FR-*)
- Define non-functional requirements (NFR-*)
- Define data requirements (DR-*)
- Get stakeholder approval

### 2. Design Phase
- Create architecture diagrams
- Document design decisions (ADRs)
- Define component interfaces
- Get technical review

### 3. Tasks Phase
- Break down into implementation tasks
- Define task dependencies
- Estimate effort
- Assign priorities

### 4. Implementation Phase
- Implement tasks in dependency order
- Write tests for each task
- Update documentation
- Review and merge

## Benefits

✅ **Traceability**: Every feature traces back to a requirement
✅ **Clarity**: Clear understanding of what to build and why
✅ **Onboarding**: New contributors understand the system quickly
✅ **Decision History**: ADRs document why choices were made
✅ **Parallel Work**: Tasks can be implemented concurrently

## Resources

- [cc-sdd Documentation](https://github.com/gotalab/cc-sdd)
- [Spec-Driven Guide](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/spec-driven.md)
- [Command Reference](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/command-reference.md)
