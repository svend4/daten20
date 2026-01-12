#compdef doc-processor.py doc-comparator.py doc-anonymizer.py doc-quality.py doc-merger.py doc-splitter.py doc-search.py doc-batch-processor.py doc-master.py doc-dashboard.py doc-api-server.py
# Zsh completion for doc-* tools
#
# Installation:
#   # System-wide:
#   sudo cp completions/doc-tools-completion.zsh /usr/share/zsh/site-functions/_doc-tools
#   # Or user-level:
#   mkdir -p ~/.zsh/completion
#   cp completions/doc-tools-completion.zsh ~/.zsh/completion/_doc-tools
#   # Add to ~/.zshrc:
#   fpath=(~/.zsh/completion $fpath)
#   autoload -U compinit && compinit

# doc-processor.py completion
_doc-processor.py() {
    local line state

    _arguments -C \
        '1: :->command' \
        '*::arg:->args'

    case $state in
        command)
            _values 'commands' \
                'process[Process single document]' \
                'ner[Extract named entities]' \
                'classify[Classify document]' \
                'relations[Extract relations]' \
                'batch[Batch process documents]' \
                'analyze[Full document analysis]'
            ;;
        args)
            case ${line[1]} in
                process|ner|classify|relations|analyze)
                    _arguments \
                        '--output[Output file]:file:_files' \
                        '--format[Output format]:(txt html markdown json)' \
                        '--lang[Language]:(en de ru)' \
                        '--help[Show help message]'
                    ;;
                batch)
                    _arguments \
                        '--output[Output directory]:directory:_directories' \
                        '--format[Output format]:(txt html markdown json)' \
                        '--recursive[Process recursively]' \
                        '--help[Show help message]'
                    ;;
            esac
            ;;
    esac
}

# doc-comparator.py completion
_doc-comparator.py() {
    local line state

    _arguments -C \
        '1: :->command' \
        '*::arg:->args'

    case $state in
        command)
            _values 'commands' \
                'compare[Compare two documents]'
            ;;
        args)
            _arguments \
                '1:first file:_files' \
                '2:second file:_files' \
                '--output[Output file]:file:_files' \
                '--metric[Similarity metric]:(cosine jaccard levenshtein all)' \
                '--report[Report format]:(html json txt)' \
                '--threshold[Similarity threshold]:(0.5 0.7 0.8 0.9 0.95)' \
                '--entities-only[Compare entities only]' \
                '--help[Show help message]'
            ;;
    esac
}

# doc-anonymizer.py completion
_doc-anonymizer.py() {
    local line state

    _arguments -C \
        '1: :->command' \
        '*::arg:->args'

    case $state in
        command)
            _values 'commands' \
                'scan[Scan for PII without anonymizing]' \
                'anonymize[Anonymize document]' \
                'deanonymize[De-anonymize document]' \
                'batch[Batch anonymize documents]'
            ;;
        args)
            case ${line[1]} in
                scan|anonymize)
                    _arguments \
                        '1:input file:_files' \
                        '--output[Output file]:file:_files' \
                        '--strategy[Anonymization strategy]:(redaction masking replacement pseudonymization generalization)' \
                        '--compliance[Compliance mode]:(gdpr hipaa both)' \
                        '--pii-types[PII types to detect]:(email phone name location iban date ip all)' \
                        '--mapping-file[Mapping file for reversible anonymization]:file:_files' \
                        '--audit-log[Enable audit logging]' \
                        '--help[Show help message]'
                    ;;
                deanonymize)
                    _arguments \
                        '1:input file:_files' \
                        '--output[Output file]:file:_files' \
                        '--mapping-file[Mapping file]:file:_files' \
                        '--help[Show help message]'
                    ;;
                batch)
                    _arguments \
                        '1:input directory:_directories' \
                        '--output-dir[Output directory]:directory:_directories' \
                        '--strategy[Anonymization strategy]:(redaction masking replacement pseudonymization generalization)' \
                        '--help[Show help message]'
                    ;;
            esac
            ;;
    esac
}

# doc-quality.py completion
_doc-quality.py() {
    local line state

    _arguments -C \
        '1: :->command' \
        '*::arg:->args'

    case $state in
        command)
            _values 'commands' \
                'analyze[Analyze document quality]' \
                'batch[Batch quality check]'
            ;;
        args)
            _arguments \
                '1:input file:_files' \
                '--output[Output file]:file:_files' \
                '--dimension[Quality dimension]:(completeness accuracy consistency readability timeliness all)' \
                '--format[Output format]:(json html text)' \
                '--threshold[Quality threshold]:(50 60 70 80 90)' \
                '--full[Full analysis]' \
                '--fail-on-low-quality[Fail if quality below threshold]' \
                '--help[Show help message]'
            ;;
    esac
}

# doc-merger.py completion
_doc-merger.py() {
    local line state

    _arguments -C \
        '1: :->command' \
        '*::arg:->args'

    case $state in
        command)
            _values 'commands' \
                'merge[Merge documents]' \
                'analyze[Analyze documents before merge]'
            ;;
        args)
            _arguments \
                '*:input files:_files' \
                '--output[Output file]:file:_files' \
                '--mode[Merge mode]:(simple smart chapters sections)' \
                '--format[Output format]:(txt md html pdf)' \
                '--toc[Add table of contents]' \
                '--remove-duplicates[Remove duplicate content]' \
                '--separator[Section separator]:text:' \
                '--help[Show help message]'
            ;;
    esac
}

# doc-splitter.py completion
_doc-splitter.py() {
    local line state

    _arguments -C \
        '1: :->command' \
        '*::arg:->args'

    case $state in
        command)
            _values 'commands' \
                'split[Split document]' \
                'preview[Preview split without writing]'
            ;;
        args)
            _arguments \
                '1:input file:_files' \
                '--output[Output directory]:directory:_directories' \
                '--mode[Split mode]:(lines pages chapter section delimiter smart)' \
                '--lines[Lines per part]:(10 50 100 500 1000)' \
                '--pages[Pages per part]:(10 50 100)' \
                '--max-size[Max size per part]:size:' \
                '--pattern[Delimiter pattern]:pattern:' \
                '--prefix[Output file prefix]:prefix:' \
                '--help[Show help message]'
            ;;
    esac
}

# doc-search.py completion
_doc-search.py() {
    _arguments \
        '1:search query:' \
        '--semantic[Use semantic search]' \
        '--fulltext[Use fulltext search]' \
        '--index[Index directory]:directory:_directories' \
        '--limit[Result limit]:(5 10 20 50 100)' \
        '--format[Output format]:(text json html)' \
        '--highlight[Highlight matches]' \
        '--help[Show help message]'
}

# doc-batch-processor.py completion
_doc-batch-processor.py() {
    _arguments \
        '1:input directory:_directories' \
        '--output[Output directory]:directory:_directories' \
        '--format[Output format]:(txt html markdown json pdf)' \
        '--pattern[File pattern]:(*.pdf *.txt *.docx *.md)' \
        '--recursive[Process recursively]' \
        '--workers[Number of workers]:(1 2 4 8)' \
        '--parallel[Parallel processing]' \
        '--help[Show help message]'
}

# doc-master.py completion
_doc-master.py() {
    local line state

    _arguments -C \
        '1: :->command' \
        '*::arg:->args'

    case $state in
        command)
            _values 'commands' \
                'status[Show system status]' \
                'services[List available services]' \
                'health[Health check]' \
                'pipeline[Run processing pipeline]' \
                'quick-process[Quick document processing]'
            ;;
        args)
            case ${line[1]} in
                quick-process)
                    _arguments \
                        '1:input file:_files' \
                        '--steps[Processing steps]:(parse analyze export compare anonymize quality all)' \
                        '--format[Output format]:(json yaml text)' \
                        '--help[Show help message]'
                    ;;
                *)
                    _arguments \
                        '--format[Output format]:(json yaml text)' \
                        '--detailed[Detailed output]' \
                        '--help[Show help message]'
                    ;;
            esac
            ;;
    esac
}

# doc-dashboard.py completion
_doc-dashboard.py() {
    _arguments \
        '--host[Host address]:(localhost 0.0.0.0 127.0.0.1)' \
        '--port[Port number]:(5000 8000 8080 3000)' \
        '--production[Run in production mode]' \
        '--debug[Enable debug mode]' \
        '--help[Show help message]'
}

# doc-api-server.py completion
_doc-api-server.py() {
    _arguments \
        '--host[Host address]:(localhost 0.0.0.0 127.0.0.1)' \
        '--port[Port number]:(5000 8000 8080 3000)' \
        '--workers[Number of workers]:(1 2 4 8)' \
        '--cors[Enable CORS]' \
        '--auth[Enable authentication]' \
        '--help[Show help message]'
}

# Main dispatcher
case "$service" in
    doc-processor.py)
        _doc-processor.py "$@"
        ;;
    doc-comparator.py)
        _doc-comparator.py "$@"
        ;;
    doc-anonymizer.py)
        _doc-anonymizer.py "$@"
        ;;
    doc-quality.py)
        _doc-quality.py "$@"
        ;;
    doc-merger.py)
        _doc-merger.py "$@"
        ;;
    doc-splitter.py)
        _doc-splitter.py "$@"
        ;;
    doc-search.py)
        _doc-search.py "$@"
        ;;
    doc-batch-processor.py)
        _doc-batch-processor.py "$@"
        ;;
    doc-master.py)
        _doc-master.py "$@"
        ;;
    doc-dashboard.py)
        _doc-dashboard.py "$@"
        ;;
    doc-api-server.py)
        _doc-api-server.py "$@"
        ;;
esac
