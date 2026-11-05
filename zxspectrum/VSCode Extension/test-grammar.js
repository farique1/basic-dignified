const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const textmate = require('vscode-textmate');
const oniguruma = require('vscode-oniguruma');

async function main() {
    const tasks = JSON.parse(fs.readFileSync(path.join(__dirname, '.vscode', 'tasks.json'), 'utf8'));
    const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));
    for (const language of manifest.contributes.languages) {
        assert(language.configuration.startsWith('./config/'));
        const configuration = JSON.parse(fs.readFileSync(
            path.join(__dirname, language.configuration), 'utf8'));
        assert.equal(configuration.comments.lineComment, 'REM');
        assert.deepEqual(configuration.brackets, [['(', ')'], ['[', ']'], ['{', '}']]);
    }
    assert(Array.isArray(tasks.tasks), 'Task template must contain a VS Code tasks array');
    assert(tasks.tasks.some(task => task.args.includes('zxspectrum.dignifier')));
    for (const task of tasks.tasks.filter(task =>
        task.args.includes('-id') || task.args.includes('zxspectrum.dignifier'))) {
        const modelIndex = task.args.indexOf('--sp_model');
        assert(modelIndex >= 0, `${task.label} must pass the selected Spectrum model`);
        assert.equal(task.args[modelIndex + 1], '${config:spectrum-basic.model}');
    }
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
        const native = 'RUN:LIST:NEW:CONTINUE:OUT 254,BIN 1010';
        const nativeTokens = grammar.tokenizeLine(native).tokens;
        const nativeAt = index => nativeTokens.find(
            token => token.startIndex <= index && token.endIndex > index).scopes;
        for (const command of ['RUN', 'LIST', 'NEW', 'CONTINUE', 'OUT']) {
            assert(nativeAt(native.indexOf(command)).includes('keyword.control.basic.spectrum'));
        }
        assert(nativeAt(native.indexOf('BIN')).includes('keyword.operator.basic.spectrum'));
        assert(nativeAt(native.indexOf('1010')).includes('constant.numeric.basic.spectrum'));
        const graphics = String.raw`PRINT "\8F%A%%\\": REM \{0D}%U`;
        const graphicTokens = grammar.tokenizeLine(graphics).tokens;
        for (const escape of [String.raw`\8F`, '%A', '%%', String.raw`\\`,
                              String.raw`\{0D}`, '%U']) {
            const index = graphics.indexOf(escape);
            assert(graphicTokens.find(token => token.startIndex <= index
                && token.endIndex > index).scopes.includes('constant.character.escape'));
        }
        assert(grammar.tokenizeLine('REMX 1000,256').tokens[0].scopes
            .includes('keyword.control.basic.spectrum'));
        const extended = String.raw`\{F5}"\{00}":DEF FN f(x)=x:SAVE "P" LINE 10:OPEN#4,"S"`;
        const extendedTokens = grammar.tokenizeLine(extended).tokens;
        const extendedAt = index => extendedTokens.find(
            token => token.startIndex <= index && token.endIndex > index).scopes;
        for (const escape of [String.raw`\{F5}`, String.raw`\{00}`]) {
            assert(extendedAt(extended.indexOf(escape)).includes('constant.character.escape'));
        }
        for (const command of ['DEF FN', 'SAVE', 'LINE', 'OPEN']) {
            assert(extendedAt(extended.indexOf(command)).includes('keyword.control.basic.spectrum'));
        }
        const rawRem = grammar.tokenizeLine(String.raw`\{EA} 123:FN`).tokens;
        assert(rawRem.every(token => token.scopes.includes('comment.line.basic.spectrum')));
        const model128 = 'PLAY "a4","b4","c4":SPECTRUM';
        const model128Tokens = grammar.tokenizeLine(model128).tokens;
        for (const command of ['PLAY', 'SPECTRUM']) {
            const index = model128.indexOf(command);
            assert(model128Tokens.find(token => token.startIndex <= index
                && token.endIndex > index).scopes.includes('keyword.control.basic.spectrum'));
        }
    }
    registry.dispose();
    console.log('Task model selection and both grammars: strings, REM, functions, native commands, BIN and 128K verified.');
}

main().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
