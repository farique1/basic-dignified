const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const textmate = require('vscode-textmate');
const oniguruma = require('vscode-oniguruma');

async function main() {
    const bytes = fs.readFileSync(require.resolve('vscode-oniguruma/release/onig.wasm'));
    await oniguruma.loadWASM(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength));
    const registry = new textmate.Registry({
        onigLib: Promise.resolve({
            createOnigScanner: patterns => new oniguruma.OnigScanner(patterns),
            createOnigString: value => new oniguruma.OnigString(value)
        }),
        loadGrammar: async scope => {
            const name = scope === 'source.basic.spectrum.classic'
                ? 'classic.tmLanguage.json' : 'spectrum.tmLanguage.json';
            return textmate.parseRawGrammar(
                fs.readFileSync(path.join(__dirname, 'syntaxes', name), 'utf8'), name);
        }
    });
    for (const scope of ['source.basic.spectrum', 'source.basic.spectrum.classic']) {
        const grammar = await registry.loadGrammar(scope);
        const line = 'PRINT "REM ""HI"" 123"; LEN a$: REM 456';
        const tokens = grammar.tokenizeLine(line).tokens;
        const at = index => tokens.find(token => token.startIndex <= index && token.endIndex > index).scopes;
        assert(at(line.indexOf('REM')).includes('string.quoted.double.basic.spectrum'));
        assert(at(line.indexOf('""')).includes('constant.character.escape'));
        assert(at(line.indexOf('LEN')).includes('support.function.basic.spectrum'));
        assert(at(line.lastIndexOf('REM')).includes('comment.line.basic.spectrum'));
        assert(!at(line.indexOf('123')).includes('constant.numeric.basic.spectrum'));
    }
    registry.dispose();
    console.log('Both grammars: doubled quotes, REM isolation, strings and native functions verified.');
}

main().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
