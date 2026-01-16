# Bash completion for Document Management System
# Source this file in your ~/.bashrc or save to /etc/bash_completion.d/

_dms_completion() {
    local cur prev words cword
    _init_completion || return

    local tools="doc-processor doc-comparator doc-anonymizer doc-quality doc-master doc-search doc-dashboard doc-api-server doc-batch-processor doc-merger doc-splitter"

    # Complete tool names
    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "$tools" -- "$cur") )
        return
    fi

    local tool="${words[1]}"

    case "$tool" in
        doc-processor)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "process batch validate" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "--output --format --quality --verbose" -- "$cur") )
            fi
            ;;
        doc-comparator)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "compare versions entities semantic" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "--report --output --threshold --verbose" -- "$cur") )
            fi
            ;;
        doc-anonymizer)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "anonymize scan deanonymize batch" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "--strategy --compliance --reversible --output" -- "$cur") )
            fi
            ;;
        doc-quality)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "analyze batch report" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "--dimensions --threshold --output --format" -- "$cur") )
            fi
            ;;
        doc-master)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "status health quick-process pipeline" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "--verbose --json --steps --output" -- "$cur") )
            fi
            ;;
        doc-search)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "search index query" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "--query --limit --format --output" -- "$cur") )
            fi
            ;;
        doc-dashboard)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "start stop status" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "--port --host --debug" -- "$cur") )
            fi
            ;;
        doc-api-server)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "start stop status" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "--port --host --workers --debug" -- "$cur") )
            fi
            ;;
        doc-batch-processor)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "process status cancel" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "--input --output --workers --format" -- "$cur") )
            fi
            ;;
        doc-merger)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "merge batch" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "--output --format --order --verbose" -- "$cur") )
            fi
            ;;
        doc-splitter)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "split batch" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "--output --method --size --verbose" -- "$cur") )
            fi
            ;;
    esac
}

# Register completion for all tools
complete -F _dms_completion doc-processor
complete -F _dms_completion doc-comparator
complete -F _dms_completion doc-anonymizer
complete -F _dms_completion doc-quality
complete -F _dms_completion doc-master
complete -F _dms_completion doc-search
complete -F _dms_completion doc-dashboard
complete -F _dms_completion doc-api-server
complete -F _dms_completion doc-batch-processor
complete -F _dms_completion doc-merger
complete -F _dms_completion doc-splitter

