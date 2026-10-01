#!/usr/bin/env bash
# Runs every SDK against the same mock API and verifies each one sends the identical 28-request sequence.
#
# Layout: put this repo and the SDK repos side by side:
#   workspace/{buyproxy-sdks,buyproxy-node,buyproxy-python,buyproxy-go,buyproxy-php,buyproxy-ruby,buyproxy-java,buyproxy-dotnet,buyproxy-rust}
# Then:  ./run-all.sh            (all languages)   ·   ./run-all.sh node python   (a subset)
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$HERE/../.." && pwd)"
# The smoke scripts reach the SDKs as ../buyproxy-*, so run them from a real folder inside the workspace.
mkdir -p "$WORKSPACE/_conformance" && cp -R "$HERE/." "$WORKSPACE/_conformance/"
cd "$WORKSPACE/_conformance"
export PORT="${PORT:-4010}"
cp="$(cd "$WORKSPACE/buyproxy-java" 2>/dev/null && mvn -q dependency:build-classpath -Dmdep.outputFile=/dev/stdout 2>/dev/null | tail -1)"

run() {  # run <name> <command...>
  printf '\n▸ %s\n' "$1"; shift
  ./run.sh "$@" 2>&1 | grep -v "Picked up"
}

LANGS=("$@"); [ ${#LANGS[@]} -eq 0 ] && LANGS=(node python go rust php ruby java dotnet)


for l in "${LANGS[@]}"; do
  case "$l" in
    node)   (cd "$WORKSPACE/buyproxy-node" && npm run -s build) >/dev/null; run node node node-smoke.mjs ;;
    python) run python python3 -c "import sys; sys.path.insert(0,'$WORKSPACE/buyproxy-python/src'); exec(open('python_smoke.py').read())" ;;
    go)     run go sh -c "cd go-smoke && go run ." ;;
    rust)   run rust sh -c "cd rust-smoke && cargo run -q" ;;
    php)    (cd "$WORKSPACE/buyproxy-php" && composer install -q --no-interaction) >/dev/null; run php php php_smoke.php ;;
    ruby)   run ruby ruby ruby_smoke.rb ;;
    java)   (cd "$WORKSPACE/buyproxy-java" && mvn -q package -DskipTests -Dmaven.javadoc.skip=true) >/dev/null
            mkdir -p java-out && javac -cp "$WORKSPACE/buyproxy-java/target/classes:$cp" -d java-out JavaSmoke.java 2>&1 | grep -v "Picked up"
            run java java -cp "java-out:$WORKSPACE/buyproxy-java/target/classes:$cp" JavaSmoke ;;
    dotnet) dotnet build dotnet-smoke -c Release -v q >/dev/null; run dotnet dotnet dotnet-smoke/bin/Release/net8.0/dotnet-smoke.dll ;;
    *) echo "unknown language: $l" ;;
  esac
done
