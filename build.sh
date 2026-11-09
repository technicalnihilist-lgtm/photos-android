#!/usr/bin/env bash
# Builds Photos.apk without Gradle: aapt2 -> javac -> d8 -> zipalign -> apksigner.
#
# Requirements:
#   - JDK 17 on PATH (or JAVA_HOME set)
#   - ANDROID_HOME pointing at an SDK with:
#       platforms;android-34  and  build-tools;34.0.0
#
# Usage: ./build.sh   (writes ./Photos.apk)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
APP="$ROOT/app"
SDK="${ANDROID_HOME:?set ANDROID_HOME to your Android SDK path}"
BT="$SDK/build-tools/34.0.0"
PLATFORM="$SDK/platforms/android-34/android.jar"
OUT="$ROOT/build"

[ -f "$PLATFORM" ] || { echo "missing $PLATFORM" >&2; exit 1; }

rm -rf "$OUT"
mkdir -p "$OUT/classes" "$OUT/gen"

echo "==> aapt2 compile"
"$BT/aapt2" compile --dir "$APP/res" -o "$OUT/res.zip"

echo "==> aapt2 link"
"$BT/aapt2" link -o "$OUT/app-unsigned.apk" \
  -I "$PLATFORM" \
  --manifest "$APP/AndroidManifest.xml" \
  -R "$OUT/res.zip" \
  -A "$APP/assets" \
  --java "$OUT/gen" \
  --min-sdk-version 24 --target-sdk-version 34 \
  --version-code 1 --version-name 1.0 \
  --auto-add-overlay

echo "==> javac"
javac -source 8 -target 8 -nowarn -bootclasspath "$PLATFORM" \
  -d "$OUT/classes" $(find "$APP/src" -name '*.java')

echo "==> d8"
"$BT/d8" -JXmx600m --release --lib "$PLATFORM" --min-api 24 \
  --output "$OUT" $(find "$OUT/classes" -name '*.class')

echo "==> package dex"
cp "$OUT/app-unsigned.apk" "$OUT/app-dex.apk"
( cd "$OUT" && zip -q app-dex.apk classes.dex )

echo "==> zipalign"
"$BT/zipalign" -f -p 4 "$OUT/app-dex.apk" "$OUT/app-aligned.apk"

if [ ! -f "$ROOT/debug.keystore" ]; then
  echo "==> generate debug keystore"
  keytool -genkeypair -keystore "$ROOT/debug.keystore" \
    -storepass android -keypass android \
    -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10950 \
    -dname "CN=Android Debug,O=Android,C=US"
fi

echo "==> apksigner"
"$BT/apksigner" sign --ks "$ROOT/debug.keystore" \
  --ks-pass pass:android --key-pass pass:android \
  --ks-key-alias androiddebugkey --min-sdk-version 24 \
  --out "$ROOT/Photos.apk" "$OUT/app-aligned.apk"
"$BT/apksigner" verify --print-certs "$ROOT/Photos.apk" | head -4

echo "built: $ROOT/Photos.apk"
