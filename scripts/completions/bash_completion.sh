#!/bin/bash
# Bash completion for daten20 CLI tools
# Source this file in your .bashrc or .bash_profile

# ============================================================================
# Completion for doc-comparator.py
# ============================================================================
_doc_comparator_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="compare analyze batch help"

    # Options for compare command
    local compare_opts="--method --threshold --output --format --verbose --help"

    # Methods
    local methods="cosine jaccard levenshtein entity all"

    # Formats
    local formats="json html text"

    case "${prev}" in
        compare|analyze)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --method)
            COMPREPLY=( $(compgen -W "${methods}" -- ${cur}) )
            return 0
            ;;
        --format)
            COMPREPLY=( $(compgen -W "${formats}" -- ${cur}) )
            return 0
            ;;
        --output)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        *)
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${compare_opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            fi
            return 0
            ;;
    esac
}

# ============================================================================
# Completion for doc-anonymizer.py
# ============================================================================
_doc_anonymizer_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="scan anonymize deanonymize batch help"

    # Options
    local opts="--strategy --compliance --reversible --mapping --output --format --help"

    # Strategies
    local strategies="redaction masking replacement pseudonymization generalization"

    # Compliance modes
    local compliance="gdpr hipaa pci ccpa"

    case "${prev}" in
        scan|anonymize|deanonymize)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --strategy)
            COMPREPLY=( $(compgen -W "${strategies}" -- ${cur}) )
            return 0
            ;;
        --compliance)
            COMPREPLY=( $(compgen -W "${compliance}" -- ${cur}) )
            return 0
            ;;
        --mapping|--output)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        *)
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            fi
            return 0
            ;;
    esac
}

# ============================================================================
# Completion for doc-quality.py
# ============================================================================
_doc_quality_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="analyze batch report help"

    # Options
    local opts="--dimensions --threshold --output --format --full --help"

    # Dimensions
    local dimensions="completeness accuracy consistency readability timeliness all"

    case "${prev}" in
        analyze|batch)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --dimensions)
            COMPREPLY=( $(compgen -W "${dimensions}" -- ${cur}) )
            return 0
            ;;
        --output)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        *)
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            fi
            return 0
            ;;
    esac
}

# ============================================================================
# Completion for doc-master.py
# ============================================================================
_doc_master_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="status services health pipeline quick-process help"

    # Options
    local opts="--format --verbose --output --steps --help"

    # Steps
    local steps="parse extract classify export all"

    case "${prev}" in
        quick-process)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --steps)
            COMPREPLY=( $(compgen -W "${steps}" -- ${cur}) )
            return 0
            ;;
        *)
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            fi
            return 0
            ;;
    esac
}

# ============================================================================
# Completion for doc-processor.py
# ============================================================================
_doc_processor_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="process extract validate export help"

    # Options
    local opts="--input --output --format --extract-entities --validate --verbose --help"

    # Formats
    local formats="json txt html pdf docx"

    case "${prev}" in
        process|extract|validate)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --format)
            COMPREPLY=( $(compgen -W "${formats}" -- ${cur}) )
            return 0
            ;;
        --input|--output)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        *)
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            fi
            return 0
            ;;
    esac
}

# ============================================================================
# Completion for doc-search.py
# ============================================================================
_doc_search_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="search index query help"

    # Options
    local opts="--query --type --limit --output --format --help"

    # Search types
    local types="keyword semantic fuzzy advanced"

    case "${prev}" in
        --type)
            COMPREPLY=( $(compgen -W "${types}" -- ${cur}) )
            return 0
            ;;
        *)
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            fi
            return 0
            ;;
    esac
}

# ============================================================================
# Completion for doc-merger.py
# ============================================================================
_doc_merger_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="merge combine help"

    # Options
    local opts="--output --format --toc --bookmarks --help"

    case "${prev}" in
        merge|combine)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --output)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        *)
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            fi
            return 0
            ;;
    esac
}

# ============================================================================
# Completion for doc-splitter.py
# ============================================================================
_doc_splitter_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="split extract help"

    # Options
    local opts="--output-dir --by --pages --size --help"

    # Split methods
    local methods="pages size bookmarks"

    case "${prev}" in
        split|extract)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --by)
            COMPREPLY=( $(compgen -W "${methods}" -- ${cur}) )
            return 0
            ;;
        --output-dir)
            COMPREPLY=( $(compgen -d -- ${cur}) )
            return 0
            ;;
        *)
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            fi
            return 0
            ;;
    esac
}

# ============================================================================
# Completion for dms-admin.py
# ============================================================================
_dms_admin_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="users documents backup restore stats help"

    # Options
    local opts="--user --action --output --format --help"

    # Actions
    local actions="create delete update list"

    case "${prev}" in
        --action)
            COMPREPLY=( $(compgen -W "${actions}" -- ${cur}) )
            return 0
            ;;
        *)
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            fi
            return 0
            ;;
    esac
}

# ============================================================================
# Completion for enterprise-admin.py
# ============================================================================
_enterprise_admin_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="tenants billing analytics reports help"

    # Options
    local opts="--tenant --action --output --format --period --help"

    # Actions
    local actions="create delete update list stats"

    # Periods
    local periods="daily weekly monthly yearly"

    case "${prev}" in
        --action)
            COMPREPLY=( $(compgen -W "${actions}" -- ${cur}) )
            return 0
            ;;
        --period)
            COMPREPLY=( $(compgen -W "${periods}" -- ${cur}) )
            return 0
            ;;
        *)
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            fi
            return 0
            ;;
    esac
}

# ============================================================================
# Register completions for all tools
# ============================================================================

# Python scripts
complete -F _doc_comparator_completion doc-comparator.py
complete -F _doc_anonymizer_completion doc-anonymizer.py
complete -F _doc_quality_completion doc-quality.py
complete -F _doc_master_completion doc-master.py
complete -F _doc_processor_completion doc-processor.py
complete -F _doc_search_completion doc-search.py
complete -F _doc_merger_completion doc-merger.py
complete -F _doc_splitter_completion doc-splitter.py
complete -F _dms_admin_completion dms-admin.py
complete -F _enterprise_admin_completion enterprise-admin.py

# Also complete when called with python
complete -F _doc_comparator_completion python\ doc-comparator.py
complete -F _doc_anonymizer_completion python\ doc-anonymizer.py
complete -F _doc_quality_completion python\ doc-quality.py
complete -F _doc_master_completion python\ doc-master.py
complete -F _doc_processor_completion python\ doc-processor.py
complete -F _doc_search_completion python\ doc-search.py
complete -F _doc_merger_completion python\ doc-merger.py
complete -F _doc_splitter_completion python\ doc-splitter.py
complete -F _dms_admin_completion python\ dms-admin.py
complete -F _enterprise_admin_completion python\ enterprise-admin.py

# Also complete when called with python3
complete -F _doc_comparator_completion python3\ doc-comparator.py
complete -F _doc_anonymizer_completion python3\ doc-anonymizer.py
complete -F _doc_quality_completion python3\ doc-quality.py
complete -F _doc_master_completion python3\ doc-master.py
complete -F _doc_processor_completion python3\ doc-processor.py
complete -F _doc_search_completion python3\ doc-search.py
complete -F _doc_merger_completion python3\ doc-merger.py
complete -F _doc_splitter_completion python3\ doc-splitter.py
complete -F _dms_admin_completion python3\ dms-admin.py
complete -F _enterprise_admin_completion python3\ enterprise-admin.py

echo "✓ daten20 CLI completions loaded"
echo "  Available tools: doc-comparator, doc-anonymizer, doc-quality, doc-master, and more"
echo "  Try: doc-comparator.py <TAB>"
