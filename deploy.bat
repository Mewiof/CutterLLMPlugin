@echo off
copy LLMPlugin.py "%APPDATA%\rizin\cutter\plugins\python"
mkdir "%APPDATA%\rizin\cutter\plugins\LLMPluginAssets"
copy Node\index.js "%APPDATA%\rizin\cutter\plugins\LLMPluginAssets\index.js"
