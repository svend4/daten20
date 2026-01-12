#!/usr/bin/env bash
# Bash completion for doc-* tools
#
# Installation:
#   sudo cp completions/doc-tools-completion.bash /etc/bash_completion.d/
#   # Or for user-level:
#   mkdir -p ~/.bash_completion.d
#   cp completions/doc-tools-completion.bash ~/.bash_completion.d/
#   echo 'source ~/.bash_completion.d/doc-tools-completion.bash' >> ~/.bashrc
#   source ~/.bashrc

# doc-processor.py completion
_doc_processor() {
    local cur prev opts cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    cmds="process ner classify relations batch analyze"

    # Get current command if any
    local cmd=""
    for ((i=1; i<${#COMP_WORDS[@]}-1; i++)); do
        case "${COMP_WORDS[i]}" in
            process|ner|classify|relations|batch|analyze)
                cmd="${COMP_WORDS[i]}"
                break
                ;;
        esac
    done

    # If no command yet, show commands
    if [[ -z "$cmd" ]]; then
        COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
        return 0
    fi

    # Command-specific options
    case "${prev}" in
        --output|-o)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --format)
            COMPREPLY=( $(compgen -W "txt html markdown json" -- ${cur}) )
            return 0
            ;;
        --lang|--language)
            COMPREPLY=( $(compgen -W "en de ru" -- ${cur}) )
            return 0
            ;;
    esac

    # General options
    opts="--output --format --lang --help -h"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}
complete -F _doc_processor doc-processor.py

# doc-comparator.py completion
_doc_comparator() {
    local cur prev opts cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    cmds="compare"

    case "${prev}" in
        --output|-o)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --metric)
            COMPREPLY=( $(compgen -W "cosine jaccard levenshtein all" -- ${cur}) )
            return 0
            ;;
        --report)
            COMPREPLY=( $(compgen -W "html json txt" -- ${cur}) )
            return 0
            ;;
        --threshold)
            COMPREPLY=( $(compgen -W "0.5 0.7 0.8 0.9 0.95" -- ${cur}) )
            return 0
            ;;
    esac

    # Get current command
    local cmd=""
    for ((i=1; i<${#COMP_WORDS[@]}-1; i++)); do
        if [[ "${COMP_WORDS[i]}" == "compare" ]]; then
            cmd="compare"
            break
        fi
    done

    if [[ -z "$cmd" ]]; then
        COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
        return 0
    fi

    opts="--output --metric --report --threshold --entities-only --help -h"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}
complete -F _doc_comparator doc-comparator.py

# doc-anonymizer.py completion
_doc_anonymizer() {
    local cur prev opts cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    cmds="scan anonymize deanonymize batch"

    case "${prev}" in
        --output|-o)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --strategy)
            COMPREPLY=( $(compgen -W "redaction masking replacement pseudonymization generalization" -- ${cur}) )
            return 0
            ;;
        --compliance)
            COMPREPLY=( $(compgen -W "gdpr hipaa both" -- ${cur}) )
            return 0
            ;;
        --pii-types)
            COMPREPLY=( $(compgen -W "email phone name location iban date ip all" -- ${cur}) )
            return 0
            ;;
    esac

    local cmd=""
    for ((i=1; i<${#COMP_WORDS[@]}-1; i++)); do
        case "${COMP_WORDS[i]}" in
            scan|anonymize|deanonymize|batch)
                cmd="${COMP_WORDS[i]}"
                break
                ;;
        esac
    done

    if [[ -z "$cmd" ]]; then
        COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
        return 0
    fi

    opts="--output --strategy --compliance --pii-types --mapping-file --audit-log --help -h"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}
complete -F _doc_anonymizer doc-anonymizer.py

# doc-quality.py completion
_doc_quality() {
    local cur prev opts cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    cmds="analyze batch"

    case "${prev}" in
        --output|-o)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --dimension)
            COMPREPLY=( $(compgen -W "completeness accuracy consistency readability timeliness all" -- ${cur}) )
            return 0
            ;;
        --format)
            COMPREPLY=( $(compgen -W "json html text" -- ${cur}) )
            return 0
            ;;
        --threshold)
            COMPREPLY=( $(compgen -W "50 60 70 80 90" -- ${cur}) )
            return 0
            ;;
    esac

    local cmd=""
    for ((i=1; i<${#COMP_WORDS[@]}-1; i++)); do
        case "${COMP_WORDS[i]}" in
            analyze|batch)
                cmd="${COMP_WORDS[i]}"
                break
                ;;
        esac
    done

    if [[ -z "$cmd" ]]; then
        COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
        return 0
    fi

    opts="--output --dimension --format --threshold --full --fail-on-low-quality --help -h"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}
complete -F _doc_quality doc-quality.py

# doc-merger.py completion
_doc_merger() {
    local cur prev opts cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    cmds="merge analyze"

    case "${prev}" in
        --output|-o)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --mode)
            COMPREPLY=( $(compgen -W "simple smart chapters sections" -- ${cur}) )
            return 0
            ;;
        --format)
            COMPREPLY=( $(compgen -W "txt md html pdf" -- ${cur}) )
            return 0
            ;;
    esac

    local cmd=""
    for ((i=1; i<${#COMP_WORDS[@]}-1; i++)); do
        case "${COMP_WORDS[i]}" in
            merge|analyze)
                cmd="${COMP_WORDS[i]}"
                break
                ;;
        esac
    done

    if [[ -z "$cmd" ]]; then
        COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
        return 0
    fi

    opts="--output --mode --format --toc --remove-duplicates --separator --help -h"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}
complete -F _doc_merger doc-merger.py

# doc-splitter.py completion
_doc_splitter() {
    local cur prev opts cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    cmds="split preview"

    case "${prev}" in
        --output|-o)
            COMPREPLY=( $(compgen -d -- ${cur}) )
            return 0
            ;;
        --mode)
            COMPREPLY=( $(compgen -W "lines pages chapter section delimiter smart" -- ${cur}) )
            return 0
            ;;
        --lines|--pages|--max-size)
            # Suggest common values
            COMPREPLY=( $(compgen -W "10 50 100 500 1000" -- ${cur}) )
            return 0
            ;;
    esac

    local cmd=""
    for ((i=1; i<${#COMP_WORDS[@]}-1; i++)); do
        case "${COMP_WORDS[i]}" in
            split|preview)
                cmd="${COMP_WORDS[i]}"
                break
                ;;
        esac
    done

    if [[ -z "$cmd" ]]; then
        COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
        return 0
    fi

    opts="--output --mode --lines --pages --max-size --pattern --prefix --help -h"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}
complete -F _doc_splitter doc-splitter.py

# doc-search.py completion
_doc_search() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    case "${prev}" in
        --index)
            COMPREPLY=( $(compgen -d -- ${cur}) )
            return 0
            ;;
        --limit)
            COMPREPLY=( $(compgen -W "5 10 20 50 100" -- ${cur}) )
            return 0
            ;;
        --format)
            COMPREPLY=( $(compgen -W "text json html" -- ${cur}) )
            return 0
            ;;
    esac

    opts="--semantic --fulltext --index --limit --format --highlight --help -h"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}
complete -F _doc_search doc-search.py

# doc-batch-processor.py completion
_doc_batch_processor() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    case "${prev}" in
        --output|-o)
            COMPREPLY=( $(compgen -d -- ${cur}) )
            return 0
            ;;
        --format)
            COMPREPLY=( $(compgen -W "txt html markdown json pdf" -- ${cur}) )
            return 0
            ;;
        --pattern)
            COMPREPLY=( $(compgen -W "*.pdf *.txt *.docx *.md" -- ${cur}) )
            return 0
            ;;
        --workers)
            COMPREPLY=( $(compgen -W "1 2 4 8" -- ${cur}) )
            return 0
            ;;
    esac

    opts="--output --format --pattern --recursive --workers --parallel --help -h"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}
complete -F _doc_batch_processor doc-batch-processor.py

# doc-master.py completion
_doc_master() {
    local cur prev opts cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    cmds="status services health pipeline quick-process"

    case "${prev}" in
        --steps)
            COMPREPLY=( $(compgen -W "parse analyze export compare anonymize quality all" -- ${cur}) )
            return 0
            ;;
        --format)
            COMPREPLY=( $(compgen -W "json yaml text" -- ${cur}) )
            return 0
            ;;
    esac

    local cmd=""
    for ((i=1; i<${#COMP_WORDS[@]}-1; i++)); do
        case "${COMP_WORDS[i]}" in
            status|services|health|pipeline|quick-process)
                cmd="${COMP_WORDS[i]}"
                break
                ;;
        esac
    done

    if [[ -z "$cmd" ]]; then
        COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
        return 0
    fi

    opts="--steps --format --detailed --help -h"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}
complete -F _doc_master doc-master.py

# doc-dashboard.py completion
_doc_dashboard() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    case "${prev}" in
        --host)
            COMPREPLY=( $(compgen -W "localhost 0.0.0.0 127.0.0.1" -- ${cur}) )
            return 0
            ;;
        --port)
            COMPREPLY=( $(compgen -W "5000 8000 8080 3000" -- ${cur}) )
            return 0
            ;;
    esac

    opts="--host --port --production --debug --help -h"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}
complete -F _doc_dashboard doc-dashboard.py

# doc-api-server.py completion
_doc_api_server() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    case "${prev}" in
        --host)
            COMPREPLY=( $(compgen -W "localhost 0.0.0.0 127.0.0.1" -- ${cur}) )
            return 0
            ;;
        --port)
            COMPREPLY=( $(compgen -W "5000 8000 8080 3000" -- ${cur}) )
            return 0
            ;;
    esac

    opts="--host --port --workers --cors --auth --help -h"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}
complete -F _doc_api_server doc-api-server.py

# Helper function to show completion info
_doc_tools_help() {
    cat <<EOF
Doc-tools Bash Completion Enabled!

Available tools with completion:
  - doc-processor.py       (process, ner, classify, relations, batch, analyze)
  - doc-comparator.py      (compare)
  - doc-anonymizer.py      (scan, anonymize, deanonymize, batch)
  - doc-quality.py         (analyze, batch)
  - doc-merger.py          (merge, analyze)
  - doc-splitter.py        (split, preview)
  - doc-search.py          (search with options)
  - doc-batch-processor.py (batch processing)
  - doc-master.py          (status, services, health, pipeline, quick-process)
  - doc-dashboard.py       (web dashboard)
  - doc-api-server.py      (API server)

Usage: Type 'doc-<TAB>' to see all tools, then '<tool> <TAB>' for commands/options

Examples:
  doc-processor.py pro<TAB>      # Completes to 'process'
  doc-comparator.py compare --metric <TAB>  # Shows: cosine jaccard levenshtein all
  doc-anonymizer.py anonymize --strategy <TAB>  # Shows anonymization strategies
  doc-quality.py analyze --dimension <TAB>  # Shows quality dimensions

EOF
}

# Export completion help function
alias doc-completion-help='_doc_tools_help'

echo "✅ Doc-tools bash completion loaded! Type 'doc-completion-help' for info."
