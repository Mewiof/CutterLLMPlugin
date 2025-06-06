(async () => {
	function LogError(text) {
		console.error(`Failed --> ${text}`);
	}
	if (!String.prototype.TrimStart) {
		String.prototype.TrimStart = function (toRemove) {
			if (this == null) return "";
			if (!toRemove) return this.toString();
			const str = this.toString();
			let startIndex = 0;
			const removalSet = new Set(toRemove);
			while (startIndex < str.length && removalSet.has(str[startIndex])) startIndex++;
			return str.substring(startIndex);
		};
	}
	if (!String.prototype.TrimEnd) {
		String.prototype.TrimEnd = function (toRemove) {
			if (this == null) return "";
			if (!toRemove) return this.toString();
			const str = this.toString();
			let endIndex = str.length - 1;
			const removalSet = new Set(toRemove);
			while (endIndex >= 0 && removalSet.has(str[endIndex])) endIndex--;
			return str.substring(0, endIndex + 1);
		};
	}

	const args = process.argv.slice(2);
	if (args.length < 3) {
		LogError("Missing arguments");
		process.exit(1);
	}
	const aPIKey = args[0];
	const model = args[1];
	const code = args[2];

	const FETCH_TIMEOUT = 60 * 1000;
	const controller = new AbortController();
	const timeoutId = setTimeout(() => {
		controller.abort();
	}, FETCH_TIMEOUT);

	try {
		const prompt = `You are a code conversion tool. Your ONLY task is to make the following disassembled code readable without altering its logic.
INPUT CODE:
\`\`\`cpp
${code}
\`\`\`

OUTPUT ONLY the resulting C++ code.
Do NOT include ANY introductions, explanations, notes, or markdown code fences like \`\`\`cpp or \`\`\`.`;
		const response = await fetch("https://openrouter.ai/api/v1/completions", {
			method: "POST",
			headers: {
				Authorization: `Bearer ${aPIKey}`,
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				model: model,
				prompt: prompt,
			}),
			signal: controller.signal,
		});
		clearTimeout(timeoutId);
		if (response.status !== 200) throw new Error(response.statusText);
		const data = await response.json();
		if (data.choices[0].finish_reason !== "stop" || data.choices[0].native_finish_reason !== "stop") throw new Error("Did not finish");
		// trim "```cpp"/"```" (just in case)
		console.log(data.choices[0].text.trim().TrimStart("```cpp").TrimStart("```c").TrimStart("```").TrimEnd("```").trim());
	} catch (e) {
		clearTimeout(timeoutId);
		LogError(e);
	}
})();
