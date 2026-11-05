# BASIC Dignified para ZX Spectrum: analise e plano

Data da analise: 2026-11-04. Ultima atualizacao: 2026-11-05.
Estado: marcos publicados ate modulo Spectrum v1.9.0 preview (release abaixo),
mais a entrega de branch/VSIX v1.10.0 com modelo 128K opcional (`--sp_model
48|128`). Sem nova tag/release, PR ou integracao ZX81 nesta rodada.
Os VSIX de cada maquina continuam separados; 48K/128K usam o mesmo
pacote Spectrum. resume.txt e um registro local, nao incluido no Git.

Entrega anterior verificada: [Spectrum v1.8.0](https://github.com/wilsonpilon/basic-dignified/releases/tag/spectrum-v1.8.0),
commit `4c66d4a07564018ee92411747e3dd96f1fe07636`, com 32 assets.
ZIP extraido e downloads conferidos; SHA-256 local/API/download iguais.
As seis demos e todos os binarios fornecidos foram reproduzidos.
A suite original permanece em 2.2.1. A entrega 1.9.0 acrescenta codigo e
documentacao, sem modificar tags/assets anteriores.
Release: [Spectrum v1.9.0](https://github.com/wilsonpilon/basic-dignified/releases/tag/spectrum-v1.9.0).

Atualizacao 1.2.0: usuario confirmou LOAD/LIST/RUN do hello.tap no
EightyOne. TZX padrao, cores, som, INPUT, GO SUB/RETURN e FOR/NEXT
implementados com testes. As secoes 1.1.0 abaixo sao historicas.

Atualizacao 1.3.0: strings, arrays numericos/string, slices,
DIM/DATA/READ/RESTORE, RANDOMIZE e funcoes nativas implementados.
Nomes restritos por categoria: usar DECLARE explicito para nomes longos
de strings, arrays e controles FOR/NEXT.

Atualizacao 1.4.0: LET implicito, compostos escalares com precedencia
preservada, `?` / `[?](linha,coluna)`, FUNC/RET e comandos graficos basicos.
Compostos em arrays/slices sao rejeitados para nao reavaliar indices.

Atualizacao 1.5.0: autorun opcional TAP/TZX; --em_run com perfil 48K
temporario; extensao VS Code/VSIX e templates Sublime. Launcher real
testado: janela responsiva, hello.TAP reconhecido e fechamento normal.
Em 2026-11-04, o usuario confirmou OK nos 16 testes manuais:
hello/colours/data/functions em TAP e TZX, com e sem autorun.
Isso valida as demos nesse procedimento, nao todo Sinclair BASIC.
Monitoramento automatico de execucao/erros continua pendente.

Atualizacao 1.5.1: erros fatais compartilhados de parser, lexer, arquivos e
configuracao passam a retornar 1 no Spectrum, inclusive com -vb 0.
Ajuda/versao/escrita de INI mantem sucesso 0; MSX/CoCo mantem a politica
original. Sem novos comandos, alteracoes nas fitas ou nos pacotes de editor.

Atualizacao 1.6.0: testes permanentes de encadeamento com :, IF/THEN,
strings/REM e erros apos separadores. RUN/LIST/NEW/CONTINUE/OUT e BIN
implementados, com validacao estrutural de argumentos e cache numerico
Sinclair correto para binarios 0..65535. RUN/LIST aceitam labels.
41 testes Python aprovados; VS Code/VSIX e Sublime atualizados.
Nova demo native em DSP/ASP/TAP/TZX; execucao manual ainda pendente.
DEF FN/FN fica para uma entrega propria.

Atualizacao 1.7.0: extensoes proprias DZS (Dignified) e AZS (texto numerado)
como padrao, mantendo DSP/ASP compativeis. Exemplos e editores migrados.
Z80 v3 e SNA 48K reais gerados por motor SkoolKit local e opcional,
com carga simulada pela ROM, estado validado antes de executar BASIC e
autorun preservado. TAP/TZX continuam sem dependencias extras; both continua
significando as duas fitas e all acrescenta os dois snapshots.
Motor 8.10 e 10.1 exercitados; Z80/SNA retomados para executar POKE na ROM.
49 testes aprovados com SkoolKit 10.1.
Task explicita de instalacao opcional no template VS Code; VSIX ainda
depende de Python/conversor externos. Empacotamento realmente integrado
fica para etapa final. Validacao manual EightyOne dos snapshots pendente.

Atualizacao 1.8.0: escapes \80..\8F para blocos 128..143 e %A..%U
(ou \90..\A4) para UDG 144..164, ativos em strings/REM. Literais usam
\\ e %%; REM admite bytes arbitrarios como \{XX}. REMX l,n[,c]
reserva linha absoluta, sem deslocar labels, com fill padrao '0' e
contagens em bytes decodificados. Includes, toggles, colisoes, headers e
relatorios cobertos. ROM retomou Z80/SNA, saltou REM com byte 13 e
desenhou o bloco/UDG com pixels exatos. 54 testes aprovados com motor;
sem motor, 5 integracoes puladas explicitamente.
Manuais originais integrados: secoes, exemplos e instrucoes MSX/CoCo
preservados, com tabelas, instalacao e referencias Spectrum no contexto.
Demo graphics e editores atualizados; validacao manual do demo pendente.

Atualizacao 1.9.0: itens 2, 3 e 5 do roteiro anterior implementados.
Bytes literais `\{XX}` em strings, REM e codigo, inclusive insercao bruta
fora de literais conforme confirmado pelo usuario. DEF FN/FN nativos com
slots ROM de seis bytes por parametro, nomes/argumentos numericos/string,
zero/multiplos argumentos e chamadas aninhadas. LOAD/SAVE/VERIFY/MERGE,
LINE, OPEN#/CLOSE#, streams, LPRINT/LLIST/COPY aceitos; perifericos extra
continuam fora do recorte 48K.
DignifieR AZS -> DZS com labels, encadeamento condicional preservado, REM
sem mudar o payload, numeracao regular mantida e protecao de sobrescrita.
Numeracao irregular com destinos dinamicos e rejeitada; binarios nao sao
entradas do DignifieR. A CLI valida o DZS gerado pelo conversor real.
61 testes com SkoolKit 10.1 aprovados; sem motor, seis skips explicitos.
ROM confirmou FN num/string/zero/aninhado, isolamento de x global,
bytes 0/255 em string e stream S nos dois snapshots.
Novas demos fn/streams e tarefas de DignifieR nos editores.

## Progresso da implementacao (atualizado em 2026-11-05)

O plano de analise abaixo continua como referencia de arquitetura, inclusive
com seus registros historicos. O estado atual prevalece nesta secao:

- [x] Modulo `-id zxspectrum`, versao propria 1.10.0; suite original 2.2.1.
- [x] Primeiro subconjunto 48K: PRINT, LET explicito, IF/GO TO, REM, CLS, STOP.
- [x] Escalares numericos alfanumericos longos; DECLARE explicito para snake_case.
- [x] Labels, macros, includes, booleanos e strings com aspas duplicadas.
- [x] Tokenizador Sinclair e TAP, com vetores fixos e testes de integracao.
- [x] Exemplo hello em DSP/ASP/TAP e manual aditivo, sem substituir o original.
- [x] TZX padrao e ampliacao documentada de comandos nativos.
- [x] Strings/arrays/FOR, DATA, funcoes nativas e Dignified FUNC/RET.
- [x] LET implicito, compostos escalares, PRINT AT e graficos basicos.
- [x] Autorun e launcher EightyOne com perfil isolado.
- [x] LOAD/LIST/RUN do hello inicial confirmado manualmente pelo usuario.
- [x] Pacotes de editor e distribuicao independente.
- [x] Validacao manual das quatro demos em TAP/TZX, com/sem autorun: 16 OK.
- [x] Retorno de erro consistente no fluxo Spectrum, com 35 testes aprovados.
- [x] Encadeamento com :, novos comandos e BIN, com 41 testes aprovados.
- [x] DZS/AZS como padrao, DSP/ASP compativeis, exemplos/editores migrados.
- [x] Z80/SNA 48K opcionais, validacao de carga/autorun e retomada BASIC na ROM.
- [x] Instalacao opcional explicita com o Python configurado no template VS Code.
- [x] Blocos/UDGs, tabela de conversao, escapes literais e definicao de bitmap.
- [x] REMX com linha absoluta, fill byte/caractere, colisoes e relatorios.
- [x] Manuais integrados no estilo original, sem remover secoes/exemplos MSX/CoCo.
- [x] Release 1.8.0, 32 assets e ZIP extraido verificados.
- [x] Bytes literais gerais, DEF FN/FN nativos e comandos de fita/streams 48K.
- [x] DignifieR Spectrum AZS -> DZS com validacao real e gravacao atomica.
- [x] Modelo 128K opcional (`--sp_model 48|128`/`SP_MODEL`): tokens nativos
  SPECTRUM e PLAY, restricao de UDG %T/%U no 128K, perfil EightyOne
  `Spectrum 128` proprio e bloqueio explicito de Z80/SNA com 128K
  (snapshots continuam 48K apenas). Sem alteracao no binario TAP/TZX
  (formato de fita nao distingue maquina) nem no limite de bytes do
  programa (mantido conservador, igual ao 48K, por falta de confirmacao
  do RAMTOP padrao do modo 128 BASIC). DignifieR Spectrum tambem recebeu
  `--sp_model`, propagado para sua validacao interna e para a validacao
  via subprocess, depois de um teste pego na revisao de documentacao
  mostrar que ele so aceitava fonte 48K por padrao. Validacao desta
  entrega: 68 testes Python executados, 62 aprovados e 6 pulados por
  ausencia do SkoolKit opcional. VSIX 1.10.0 com selecao de modelo
  `spectrum-basic.model`, tarefas de conversao/DignifieR e realce
  PLAY/SPECTRUM. Sem nova tag/release; Sublime anterior preservado.
- [x] VSIX Spectrum 1.10.0 gerado e inspecionado: integridade, versao,
  arquivos empacotados e aviso do bug 128K conferidos. npm test aprovado;
  tarefas extraidas do pacote converteram e dignificaram hello (48K) e
  play128 (128K) pelo conversor real. MSX/CoCo nao validados nesta rodada,
  conforme solicitado. Instalacao/teste visual no VS Code fica para o usuario.
- [ ] Validacao manual das novas demos fn/streams e comandos com midia/impressora.
- [ ] Validacao manual da nova demo graphics no EightyOne.
- [ ] Validacao manual da nova demo native (TAP/TZX, com/sem autorun).
- [ ] Validacao manual dos snapshots Z80/SNA no EightyOne.
- [x] Carga e execucao manuais de play128.tzx confirmadas pelo usuario em
  2026-11-05 no EightyOne e no Spectaculator: musica e troca final para
  48 BASIC por SPECTRUM funcionam. UDG T/U no LIST posterior sao esperados.
- [ ] Corrigir/validar lancamento automatico EightyOne 128K
  (`--sp_model 128 --em_run`): usuario relatou boot seguido de tela preta,
  sem musica e sem resposta a BREAK, liberando apenas com reset.
- [ ] Integracao automatica do Spectaculator: abertura manual documentada;
  selecao de modelo por CLI e ciclo de vida ainda nao verificados.
- [ ] VSIX realmente integrado com conversor e instalacao simplificada.
- [ ] Monitoramento automatico dos erros de execucao da ROM. Verificado:
  EightyOne nao tem gancho de automacao/depuracao externo (so GUI manual);
  o monitoramento do MSX via openMSX e exclusivo de Unix. A unica via
  viavel seria simulacao offline do SkoolKit (Simulator), continuando a
  execucao apos o LOAD e inspecionando ERR_NR/PPC na RAM — nao e
  monitorar a janela real do EightyOne. Adiado a pedido do usuario.
- [ ] Extracao/destokenizacao de BASIC em TAP/TZX/Z80/SNA.
- [ ] Snapshots Z80/SNA para o modelo 128K (formato de 8 bancos de 16K;
  comportamento do SkoolKit com `machine=128` e `get_snapshot` nao
  verificado). Bloqueado explicitamente por enquanto: `--sp_model 128`
  com `--tk_format z80/sna/all` falha com erro claro.

O detalhamento do comportamento implementado esta em
[documentation/ZX_SPECTRUM.md](documentation/ZX_SPECTRUM.md).
As propostas de "primeira entrega" do plano original abaixo abrangem o
objetivo completo; v1.1.0 implementa apenas o primeiro marco funcional.

## Pendencias priorizadas

Custos relativos estimados, nao prazos. A ordem considera necessidade
funcional antes do custo. Nesta revisao, a parte 128K do item 5 (tokens
nativos SPECTRUM/PLAY, sem snapshots/perifericos) foi implementada; os
demais itens continuam pendentes como antes, e o item 2 foi investigado
e adiado a pedido do usuario (ver justificativa abaixo da tabela).

| Ordem | Trabalho | Necessidade | Custo | Criterio de conclusao |
| :-: | :- | :-: | :-: | :- |
| 1 | Validacao manual e integracao EightyOne | Alta | Baixo para testes; correcao a investigar | Native/graphics/fn/streams, snapshots e midia/impressora com resultados registrados; play128.tzx manual aprovado no EightyOne/Spectaculator, mas launcher 128K congela |
| 2 | Monitorar erros da ROM | Media | Alto | Investigado e adiado: so viavel via simulacao offline do SkoolKit (Simulator), nao via EightyOne (sem gancho de automacao) nem via o metodo do MSX (openMSX, exclusivo de Unix) |
| 3 | Empacotamento integrado final | Alta para distribuicao final | Medio/alto | Instalar/configurar conversor e Python com fluxo simples; SkoolKit continua opcional e sem ROM embutida |
| 4 | Extrair/destokenizar binarios | Media | Alto | Recuperar AZS de TAP/TZX/Z80/SNA; converter AZS para DZS ja funciona |
| 5 | Outros modelos/perifericos | Opcional | Alto | 128K (tokens nativos) implementado; faltam seus snapshots Z80/SNA, Microdrive/disco, NextBASIC, turbo e fitas com varios arquivos |

O empacotamento integrado permanece na etapa final, conforme decidido, apesar da importancia
para novos usuarios. Publicacao em lojas de editores tambem fica para essa
etapa; os pacotes offline atuais ja estao disponiveis.

### Proxima verificacao manual

- [ ] Native: TAP e TZX, com carga manual/RUN e com autorun.
- [ ] Graphics: TAP e TZX, conferir os 16 blocos e o UDG A customizado.
- [ ] Hello e graphics: abrir Z80/SNA sem autorun, conferir LIST e executar RUN.
- [ ] Regenerar hello/graphics com autorun 0 e conferir ambos os snapshots.
- [ ] Registrar versao/perfil 48K do EightyOne, formato e resultado de cada caso.
- [ ] FN/streams: conferir resultados e bytes literais; usar midia/impressora
  apropriadas para a secao de comandos depois de STOP.
- [ ] 128K: abrir EightyOne com `--sp_model 128 --em_run` (perfil
  `eightyone128.ini`, MachineName=Spectrum 128); conferir se o menu
  128/tape loader e o autoload da fita funcionam como esperado. Testado pelo
  usuario em 2026-11-05: congela em tela preta depois do boot; pendente
  correcao, nao aprovado.
- [x] 128K manual: play128.tzx carregou e executou, tocando as notas, no
  EightyOne e no Spectaculator. SPECTRUM final muda para 48 BASIC;
  PLAY/SPECTRUM aparecem como UDG U/T no LIST desse modo, como esperado.

O usuario considerou os testes bem-sucedidos nesta rodada; o resultado
detalhado informado cobre play128.tzx manual nos dois emuladores.
Nao ha resultados individuais novos para marcar toda a matriz 48K,
snapshots e perifericos como aprovada. O launcher 128K continua com a
falha acima. Adaptacao manual para outros emuladores esta documentada em
[ZX_SPECTRUM.md](documentation/ZX_SPECTRUM.md#spectaculator-and-other-emulators).
Investigacao do Spectaculator 9.1: a associacao Windows local abre TZX via
SpecStub.exe; o manual oficial documenta File > Open e Auto load.
Nao foi estabelecida uma opcao CLI verificada para selecionar 48K/128K.
Abertura externa e simples, mas integracao completa via --em_run fica
para versao futura, sem reutilizar indevidamente o INI do EightyOne.

As fitas e snapshots fornecidos de graphics estao sem autorun; os casos
com autorun precisam ser regenerados pelas opcoes documentadas.
Os 16 OK anteriores referem-se apenas a hello/colours/data/functions em
TAP/TZX. Os testes automaticos da ROM nao substituem essa nova verificacao.

### Limites que nao sao pendencias obrigatorias

Aliases automaticos para nomes restritos, compostos em arrays/slices e
frames locais recursivos continuam fora do subconjunto atual. Nao sao
promessas de implementacao para a proxima entrega. O DignifieR MSX original
e os bugs/ideias gerais de Farique permanecem separados deste roteiro.
Recuperar AZS de TAP/TZX/Z80/SNA exige destokenizacao/extracao adicional;
AZS para DZS nao implica essa capacidade nem recupera macros e
aliases originais que se perderam na conversao.

## 1. Conclusao e escopo

**E viavel** acrescentar o Sinclair BASIC do ZX Spectrum sem substituir os
modulos MSX/CoCo e sem reescrever a suite. O carregamento por `-id` e os
hooks de linguagem/ferramentas ja constituem a maior parte da infraestrutura.
O trabalho principal sera a descricao do dialeto, suas regras de variaveis,
a tokenizacao correta e o empacotamento em fita.

Recomendacao para a primeira entrega:

- Sinclair BASIC padrao do Spectrum 48K, em ROM inglesa.
- Fonte Dignified sem numeros, com labels, macros, includes, declares,
  funcoes Dignified, variaveis longas e operadores compostos.
- Listagem classica numerada para inspecao e entrada classica por `-asc`.
- Programa tokenizado carregavel em **TAP e TZX**.
- EightyOne como primeiro emulador, com caminho configuravel.
- Preservacao do comportamento MSX/CoCo e da documentacao original.

Esse recorte de 48K e uma proposta de implementacao, nao uma limitacao
solicitada pelo usuario. Deve ser confirmado antes da implementacao.
Spectrum 128K, `PLAY`, comandos de disco/Microdrive, NextBASIC, snapshots
SNA/Z80, loaders turbo e fitas com varios arquivos ficam para etapas
posteriores, salvo redefinicao de escopo.
Tokens que existem na ROM 48K mas dependem de perifericos devem ser
reconhecidos e documentados; isso nao significa emular esses perifericos.

Nao e necessario inventar uma extensao binaria proprietaria para executar
o BASIC: TAP/TZX ja podem conter o programa tokenizado. Um dump cru seria
apenas uma saida tecnica opcional, sem promessa de carga direta no emulador.
Tambem nao e necessario produzir audio WAV para atender TAP/TZX.

## 2. Estado real do repositorio

- Branch analisado: `suporte-zx-spectrum`.
- Base atual: `4283702`, a mesma implementacao de MSX/CoCo de `main`.
- README anuncia a suite como v2.2.1; alguns cabecalhos internos ainda
  mencionam v2.0. Nenhuma versao foi alterada nesta analise.
- Nao existe pasta Spectrum neste branch.
- O branch local `suporte-zx81`, em `a9e43a5`, contem a implementacao ZX81,
  mas suas alteracoes **nao estao presentes** no branch Spectrum.
- Foram consultados arquivos do ZX81 com `git show`, sem trocar de branch,
  fazer merge ou modificar o trabalho que aguarda aprovacao.
- Nao foram encontrados testes automatizados rastreados nem configuracao
  de runner/CI no branch atual. O branch ZX81 possui seu proprio arquivo
  de testes; isso nao valida o Spectrum.
- `resume.txt` e `todo.txt` estao excluidos localmente por
  `.git/info/exclude`. Portanto `resume.txt` existe no disco, mas nao entra
  automaticamente em commits. `OUTLINE.md` nao esta excluido.
- Foi localizado `C:\zeddy\EightyOne.exe`, com FileVersion 1.41.0.0.
  Seu historico local registra suporte a varios modelos Spectrum.
  O emulador nao foi aberto nem teve sua configuracao alterada.

## 3. Como o programa funciona

### 3.1 Configuracao e descoberta de modulos

[Settings.init](support/badig_settings.py#L68) le o INI global, identifica
`-id` e importa dinamicamente:

```text
<id>.badig_<id>
<id>.tools_<id>
```

`Classic.Expose()` e `Tools.Expose()` fornecem argumentos e remtags.
`Classic.Description.sysinfo()` informa nome do sistema e extensoes;
nao existe mais necessidade de cadastrar sistemas em um JSON central.
As configuracoes especificas sao inicializadas por `Classic.Settings`.

O modulo e escolhido antes da segunda leitura de argumentos/remtags:
nao devemos depender de `##BB:arguments=-id ...` para trocar de dialeto.
O ID deve ser passado na linha de comando ou configurado no INI global.

### 3.2 Conversao da linguagem

[Main](badig.py#L1895) possui dois caminhos:

1. Dignified: carregar fonte -> lexer -> parser -> gerar listagem ->
   salvar -> executar ferramentas.
2. `-asc`: aceitar uma listagem classica ja numerada e executar ferramentas,
   sem reaplicar macros, labels, alocacao de variaveis ou renumeracao.

O lexer combina as descricoes Dignified e Classic. A descricao do sistema
controla comandos, numeros, operadores, identificadores, comentarios e
literais. O modulo pode participar pela classe `Lexer`.

[Parser.par](badig.py#L1347) organiza cinco passes:

| Etapa | Responsabilidade compartilhada |
| --- | --- |
| 1 | Toggles de comentarios, DEFINE, DECLARE, KEEP, FUNC/RET e macros |
| 2 | Chamadas de funcoes, labels, loops por labels e EXIT |
| 3 | Includes, limpeza de separadores/quebras, comentarios e uniao de strings |
| 4 | Cabecalho, numeros de linha, resolucao dos destinos e variaveis |
| 5 | Transformacoes do dialeto e capitalizacao |
| Geracao | Espacos, listagem, comentarios de labels e tamanho das linhas |

O modulo Classic fornece `Parser.initialization`, `pass_1` a `pass_5` e
`generate`. O protocolo dos hooks e: `False` prossegue normalmente,
`None` omite o token corrente e um Token pode substitui-lo.
Includes passam pelos tres primeiros passes; numeracao e resolucao final
acontecem no programa consolidado.

As funcoes Dignified sao expandidas como atribuicoes e GOSUB/RETURN;
**nao sao** as funcoes nativas `DEF FN` do Spectrum.
A compatibilidade deve incluir atribuicoes geradas pela propria suite,
nao somente as escritas diretamente pelo usuario.

### 3.3 Ferramentas e execucao

[tools_msx.Interface](msx/tools_msx.py#L7) chama primeiro o tokenizer e
depois o emulador. Se a tokenizacao foi habilitada e gerou arquivo, troca
o destino usado pelo emulador para a versao binaria.
O modulo CoCo segue o mesmo contrato.

[tokenizer_interface](msx/tokenizer_interface.py#L17) fornece
`Run`, `Expose`, `Settings` e o adaptador do tokenizador. A interface
MSX chama o MSX Batoken em Python; a CoCo usa o `decb` externo.

O openMSX tem controle remoto e monitoramento especificos.
O CoCo encapsula o programa em CAS para o XRoar.
[cocotocas.py](coco/cocotocas.py) serve como precedente arquitetural de
empacotamento, **nao** como implementacao reutilizavel do formato Spectrum.
CAS CoCo, TAP Spectrum e TZX sao formatos diferentes.

## 4. Onde encaixar o Spectrum

Estrutura proposta, ainda inexistente:

```text
zxspectrum\
    badig_zxspectrum.py
    badig_zxspectrum.ini
    tools_zxspectrum.py
    tokenizer_zxspectrum.py
    tokenizer_interface.py
    tokenizer_interface.ini
    tape_zxspectrum.py
    emulator_interface.py
    emulator_interface.ini
    test_tokenizer_zxspectrum.py
    test_tape_zxspectrum.py
    test_badig_zxspectrum.py
examples\
    zxspectrum\
```

ID recomendado: `zxspectrum`; extensoes textuais propostas: `.DSP` para
Dignified e `.ASP` para a listagem classica. Sao propostas, nao interfaces
ja disponiveis. Evitam reutilizar `.DZX`/`.AZX` do ZX81.

| Ponto existente | Uso proposto |
| --- | --- |
| `Description.sysinfo` | Nome, extensoes e `.tap` como saida binaria padrao |
| `Description.__init__` | Vocabulario, tipos, separadores e regras do Spectrum |
| `Lexer` | Literais, DATA, numeros e tokens com particularidades Sinclair |
| `Parser.initialization/pass_*` | PRINT AT, LET, nomes, aliases e booleanos |
| `Parser.generate` | Separacao lexica segura e comentarios de labels |
| `tools_zxspectrum.Interface` | Converter -> tokenizar -> gerar fitas -> emulador |
| `Expose` e INIs | CLI/remtags, formato, nome em fita, autorun e emulador |

Manter o tokenizador independente da CLI para permitir testes com
entrada textual e retorno binario. O empacotador recebe esse mesmo
payload para TAP e TZX, evitando duas implementacoes de tokenizacao.
Uma separacao simples em dois arquivos e suficiente; nao criar um
framework generico de fitas.

Manter as convencoes familiares `--tk_tokenize` e `--em_run`.
Proposta adicional a fechar na etapa 0: `--tk_format tap|tzx|both`.
Se ambos forem gerados, TAP pode ser o arquivo enviado ao EightyOne.
O caminho efetivo deve ser informado pela interface, nao reconstruido
somente com `binary_ext`, pois essa propriedade comporta uma unica extensao.
Nao iniciar o emulador sobre arquivo antigo ou parcialmente gerado.

## 5. Diferencas que impedem copiar simplesmente o MSX

### 5.1 Variaveis e espacos

O Spectrum permite nomes longos para escalares numericos, mas exige uma
letra para controle FOR/NEXT, arrays numericos e strings/arrays de strings.
O alocador MSX assume nomes significativos de dois caracteres e 676
combinacoes; o ZX81 reduz nomes a uma letra. Nenhuma dessas estrategias
deve ser adotada automaticamente como regra universal do Spectrum.

Recomendacao: reconhecer as categorias de uso, preservar escalares
alfanumericos nativos quando seguro e mapear nomes longos Dignified
restritos para uma letra. Resolver antes as colisoes, variaveis de includes,
nomes com `_`, DECLARE, `~`, FOR/NEXT e nomes usados em mais de um contexto.
Namespaces que a ROM compartilha devem continuar compartilhados.
O esgotamento das letras deve gerar erro, nunca alias silencioso.
Uma estrategia inicial que compacte todos os nomes para uma letra e
mais simples, mas impoe um limite artificial de 26 nomes numericos:
so adota-la se essa restricao for aprovada explicitamente.

O parser comum de DECLARE usa `c_var_valid_chars` e pressupoe um unico
comprimento de alias. Essa e uma area de acoplamento a avaliar com testes;
um alocador contextual pode exigir um hook opcional especifico, mantendo
o comportamento anterior como padrao para MSX/CoCo.

Espacos nao distinguem nomes de escalares na ROM. Remover espacos com
`-ss` tambem pode tornar ambiguos nomes e palavras-chave no tokenizer
textual. Testar fronteiras lexicas, palavras reservadas dentro de nomes
e identificadores que diferem apenas em caixa/espacos.
Nao substituir palavras-chave com um simples `str.replace`.

### 5.2 Sintaxe e recursos

- `GO TO`, `GO SUB`, `DEF FN`, `OPEN #` e `CLOSE #` requerem tratamento
  consistente entre texto e tokens compostos. Aceitar `GOTO`/`GOSUB`
  como aliases Dignified e gerar a grafia Sinclair e uma boa compatibilidade.
  O lexer atual le prefixos progressivamente: regex apenas para a palavra
  completa com espaco pode ser insuficiente sem tratamento de prefixos.
- `LET` e necessario na listagem Sinclair. Se atribuicoes implicitas forem
  aceitas, inseri-lo no inicio da instrucao, depois de `:` e de `THEN`,
  incluindo expansoes de macros e de funcoes. Nao inserir em IF, FOR,
  comparacoes ou argumentos de funcoes nativas.
- `IF ... THEN GO TO {label}` precisa manter THEN e o salto. As opcoes
  MSX de retirar THEN/GOTO nao podem ser copiadas; `THEN 100` nao e o
  equivalente Sinclair do comando de salto.
- O Spectrum 48K nao possui ELSE nativo. ENDIF Dignified ja e uma diretiva
  removida pelo nucleo, nao uma implementacao generica de IF em bloco.
  Nao prometer ELSE/blocos novos sem um projeto especifico.
- TRUE deve representar 1 e FALSE 0, nao o TRUE=-1 do modulo MSX.
  AND/OR/NOT seguem a semantica Sinclair, nao a logica bit a bit MSX.
- DATA aceita expressoes. O lexer MSX trata itens como literais opacos:
  copia-lo impediria converter nomes longos/macros e tokenizar expressoes.
  Distinguir ainda `DATA` de `SAVE/LOAD ... DATA a()`.
- Apostrofo em PRINT significa quebra de linha, nao comentario MSX.
  Usar REM para comentarios classicos e `: REM` no relatorio de labels.
  Depois de REM, preservar o restante, inclusive dois-pontos e aspas.
- Aspas internas sao duplicadas: `"A ""B"""`. O nucleo junta strings
  adjacentes; a leitura e essa uniao precisam preservar as aspas Sinclair.
- `[?](linha,coluna)` pode expandir para `PRINT AT linha,coluna;`.
  Explicitar a ordem: difere de LOCATE x,y do MSX.
- Cobrir cores, graficos, som e I/O: BORDER, PAPER, INK, BRIGHT, FLASH,
  INVERSE, OVER, PLOT, DRAW, CIRCLE, BEEP, IN, OUT, ATTR, SCREEN$,
  entre todos os demais tokens da ROM 48K.
- Numeros incluem notacao exponencial e `BIN`. Nao herdar silenciosamente
  os sufixos `%`, `!`, `#`, hexadecimal `&H` e demais extensoes MSX.
- Strings aceitam slicing com TO, inclusive atribuicao a substring.
  Parametros de DEF FN sao de uma letra e nao devem ser renomeados como
  variaveis comuns sem considerar seu escopo.

### 5.3 Representacao binaria

O resultado nao e um texto com comandos substituidos por bytes:

1. Linha BASIC: numero em dois bytes **big-endian**, comprimento do corpo
   em dois bytes **little-endian**, corpo tokenizado e terminador `0x0D`.
   O comprimento inclui o terminador, nao o cabecalho de quatro bytes.
2. Os tokens padrao 48K ocupam `0xA5..0xFF`. Nao reutilizar a tabela ZX81.
3. Constantes numericas em codigo tem representacao textual seguida de
   `0x0E` e cinco bytes numericos Sinclair. Cobrir inteiros compactos,
   ponto flutuante, expoentes, arredondamento e limites. Tratar o sinal
   como operador quando apropriado, nao como parte indistinta do literal.
4. Nao adicionar representacao numerica oculta a digitos dentro de strings
   ou REM, nem a digitos integrantes de nomes como `score2`.
5. A representacao interna de `DEF FN` tambem requer espaco oculto para
   os argumentos: conferir na ROM/listagem salva os marcadores e cinco
   bytes reservados. Tokenizar somente o texto visivel nao basta.
6. Caracteres nao sao Latin-1 puro: libra, copyright, mosaicos, UDG e
   controles de cor/cursor precisam de mapeamento e escapes documentados.
   Nao reaproveitar os codigos graficos ZX81.

O tokenizador deve rejeitar linhas duplicadas/fora de ordem, numeros
invalidos, caracteres sem representacao e comprimentos impossiveis.
A faixa normal de linhas digitaveis e 1..9999; arquivos tecnicos podem
conter linha 0. Fechar uma politica explicita para importacao de linha 0
e autorun, sem copiar automaticamente a permissividade do ZX81.
Passo zero e estouro de numeracao tambem precisam ser diagnosticados.

### 5.4 TAP e TZX

**TAP:** cada bloco possui comprimento de dois bytes little-endian,
flag, conteudo e checksum XOR. Para BASIC padrao:

- Header: flag `0x00`, tipo `0` (programa), nome de 10 bytes preenchido
  com espacos, tamanho dos dados, parametro de autorun e deslocamento
  para a area de variaveis, seguidos de checksum.
- O bloco de header completo tem 19 bytes, fora os dois de comprimento.
- Data: flag `0xFF`, programa tokenizado e eventuais variaveis, checksum.
- Sem variaveis pre-inicializadas, o deslocamento coincide com o tamanho
  da area de programa; nao adicionar imagem de sistema ZX81 ou seu
  marcador de fim de variaveis por analogia.
- Definir o valor de "sem autorun" e validar linha de inicio quando usado.
  Autorun no header e selecao de maquina no emulador sao coisas distintas.

**TZX:** assinatura `ZXTape!`, byte `0x1A`, versao e blocos.
A primeira implementacao pode usar apenas blocos `0x10`, Standard Speed
Data Block, com pausa e os mesmos bytes de header/data usados pelo TAP.
Nao incluir o prefixo de comprimento TAP dentro dos dados do bloco TZX:
o bloco TZX tem seus proprios campos de comprimento.
Nao ha necessidade de implementar turbo, protecao ou pulsos arbitrarios.

Validar limites de 16 bits dos blocos separadamente da memoria disponivel
no Spectrum. Um arquivo estruturalmente valido nao garante memoria para
programa, variaveis e pilhas; documentar o limite estatico e a margem
necessaria em execucao, sem prometer "48 KB livres para BASIC".

## 6. Reaproveitamento do ZX81 e mudancas minimas no nucleo

O branch ZX81 acrescenta hooks opcionais de:

- `Lexer.quoted_string`;
- `Classic.preprocess` e `Classic.postprocess`;
- deteccao/renumeracao de listagens numeradas.

Os hooks de strings sao candidatos uteis para o Spectrum. Pre/postprocess
so devem ser trazidos se houver necessidade demonstrada.
Nao fazer merge integral nem copiar o tokenizer ZX81: `.p` e uma imagem
de memoria com estruturas de sistema/display, nao um programa Spectrum
encapsulado em fita.
Tambem nao transportar `remx`, enderecos 16514 ou comandos FAST/SLOW.
O empacotamento do ponto flutuante pode servir de referencia, mas precisa
de vetores proprios, especialmente para o formato compacto de inteiros.

Acoplamentos adicionais encontrados no nucleo:

- [Parser.generate](badig.py#L1862) rejeita listagens com mais de 256
  caracteres por linha. Isso e uma regra herdada, nao o limite binario
  generico do Spectrum. Avaliar um limite opcional por dialeto, mantendo
  256 como padrao MSX/CoCo; validar separadamente bytes tokenizados.
- Uniao de strings e DECLARE precisam dos cuidados descritos acima.
- [Infolog.log](support/helper.py#L32) termina erros com `SystemExit(0)`.
  E um problema preexistente: validacoes nao podem confiar so no exit code.
  Evitar reforma global nesta entrega; definir erros proprios do novo
  tokenizer e verificar mensagem, artefatos e nao execucao do emulador.
- O lexer usa uma sentinela PROGRAM que pode aparecer no processamento
  de variaveis; existe tratamento local no ZX81. Cobrir o caso nos
  relatorios Spectrum sem atribuir a ele uma variavel real.

Cada mudanca compartilhada deve ser opcional, coberta por regressao e
apresentada separadamente das alteracoes locais do Spectrum.
Renumerar fontes classicas automaticamente e criar um DignifieR Spectrum
sao melhorias posteriores; o primeiro fluxo classico pode usar `-asc`.

## 7. EightyOne: o que sabemos e o que falta provar

O nome do emulador e **EightyOne** (o pedido menciona "EightOne").
A pagina do projeto confirma suporte a Spectrum, e a instalacao local
tambem o evidencia. Isso confirma a escolha como alvo, mas nao prova a
automacao de carregamento.

A interface ZX81 existente em outro branch executa
`[emulator_path, arquivo.p]`. Essa chamada nao seleciona explicitamente
um Spectrum e nao comprova montagem/reproducao de TAP/TZX.
Nao inventar flags de linha de comando nem assumir o protocolo openMSX.

Validacao obrigatoria antes de fechar a interface:

1. Escolher Spectrum 48K/ROM inglesa sem sobrescrever o perfil ZX81.
2. Montar um TAP conhecido; executar `LOAD ""`, reproduzir fita e verificar
   listagem/resultado. Repetir com TZX padrao.
3. Testar abertura por argumento, selecao/persistencia de maquina e
   mecanismos de autoload efetivamente suportados pela versao instalada.
4. Separar abrir emulador, montar fita, carregar BASIC e autorun.
5. Se so houver suporte manual em algum passo, informar claramente e
   documentar o procedimento; nao apresentar abertura de janela como
   execucao automatica bem-sucedida.

Nao incluir monitoramento de erros equivalente ao openMSX no MVP.
Manter relatorios de origem/linha para depuracao e possivel integracao futura.

## 8. Divisao do trabalho

Legenda: `[x]` concluido nesta analise; `[ ]` ainda nao executado.
Cada etapa abaixo deve ser uma entrega revisavel, nao um unico pacote
grande que so possa ser testado ao final.

### A. Analise e inventario

- [x] Mapear configuracao, lexer, passes, geracao e ferramentas.
- [x] Comparar pontos de extensao MSX/CoCo com o branch ZX81.
- [x] Identificar incompatibilidades Sinclair e formatos de fita.
- [x] Consultar referencias tecnicas e confirmar instalacao do EightyOne.
- [x] Criar este plano e atualizar o resumo de continuidade.
- [ ] Validar resultados em emulacao: nao realizado nesta etapa documental.

### 0. Fechar contrato do modulo

Dependencias: A.

- [ ] Confirmar 48K como alvo inicial, ID e extensoes propostas.
- [ ] Fechar politica de nomes, DECLARE/`~`, aliases, LET implicito e PRINT AT.
- [ ] Definir CLI/remtags de TAP/TZX, nome em fita e autorun.
- [ ] Fixar politica de linha 0, limites, encoding e escapes.
- [ ] Fazer a prova de carga/automacao EightyOne da secao 7.
- [ ] Preparar pequenos vetores independentes de tokenizacao/ROM.

Aceite: decisoes registradas e caminho de carga reproduzivel, ainda sem
depender de um tokenizador novo para provar que o emulador aceita as fitas.

### 1. Estrutura e descricao do dialeto

Dependencias: 0.

- [ ] Criar `zxspectrum` com Description, Settings, Expose, Lexer e Parser.
- [ ] Permitir `-id zxspectrum -h`, sem mudar o ID padrao MSX.
- [ ] Enumerar integralmente tokens 48K, operadores, numeros e comentarios.
- [ ] Adaptar somente hooks de nucleo comprovadamente necessarios.

Aceite: configuracao carrega isoladamente; MSX/CoCo conservam CLI e defaults.

### 2. Dignified -> BASIC Spectrum numerado

Dependencias: 1.

- [ ] Implementar alocacao de nomes e validacao de categorias/colisoes.
- [ ] Adaptar LET, GO TO/GO SUB, booleanos, PRINT AT e operadores compostos.
- [ ] Tratar DATA, slicing, strings com aspas duplicadas e DEF FN.
- [ ] Verificar macros, includes, funcoes Dignified, labels, loops e EXIT.
- [ ] Validar relatorios, cabecalho, `-ss`, limites de linha e de numeracao.

Aceite: listagem resultante usa sintaxe Sinclair valida e os destinos
apontam para as linhas corretas, inclusive depois dos includes/expansoes.

### 3. Tokenizador Spectrum independente

Dependencias: 0. Pode avancar em paralelo a 1/2 usando listagens classicas.

- [ ] Implementar scanner contextual: codigo, nomes, strings e REM.
- [ ] Codificar tokens, caracteres, numeros e parametros ocultos DEF FN.
- [ ] Montar linhas com endianness e comprimentos corretos.
- [ ] Rejeitar entradas invalidas sem gerar binario parcial.
- [ ] Comparar com vetores conhecidos e dados salvos pela ROM.

Aceite: igualdade de bytes nos vetores fixos; nao apenas round-trip usando
encoder e decoder novos que poderiam compartilhar o mesmo erro.

### 4. Empacotadores TAP e TZX

Dependencias: 3.

- [ ] Criar header BASIC, nome de fita, autorun e deslocamento de variaveis.
- [ ] Gerar blocos TAP com tamanho e XOR corretos.
- [ ] Gerar TZX padrao com assinatura/versao e blocos 0x10.
- [ ] Validar limite de bloco, memoria e determinismo.

Aceite: extrair TAP e TZX produz o mesmo payload BASIC; ferramenta
independente/emulador reconhece ambos como programa, nao Bytes/CODE.

### 5. Integracao CLI, INI, remtags e EightyOne

Dependencias: 2, 4 e prova de automacao da etapa 0.

- [ ] Conectar interfaces ao contrato existente de ferramentas.
- [ ] Dar suporte a Dignified e `-asc`, TAP, TZX e geracao de ambos.
- [ ] Selecionar explicitamente o artefato destinado ao emulador.
- [ ] Validar caminhos com espacos, destino, executavel e erros de processo.
- [ ] Nao apagar ASCII antes de concluir as saidas solicitadas com sucesso.
- [ ] Implementar apenas automacao comprovada; documentar passos manuais.

Aceite: comando unico gera o formato solicitado; opcao de emulador carrega
e executa conforme contrato documentado, ou informa a intervencao exigida.

### 6. Regressao e exemplos

Dependencias: 2, 3, 4, 5. Os testes focados nascem junto com cada etapa.

- [ ] Testar exemplos existentes MSX/CoCo sem mudar seus arquivos de origem.
- [ ] Criar exemplos Spectrum pequenos: hello, macros/labels/includes,
  subrotinas, DATA/arrays, cores/graficos/som e strings/UDG.
- [ ] Testar TAP e TZX no EightyOne 48K, com/sem autorun.
- [ ] Confirmar execucao de programas que contem DEF FN e numeros fracionarios.
- [ ] Registrar versao do emulador, modelo/ROM, passos e resultados reais.

Aceite: todas as verificacoes da secao 9 passam; distinguir teste automatico
de validacao manual e de funcionalidades apenas planejadas.

### 7. Documentacao aditiva e integracao com editores

Dependencias: 5 e exemplos de 6.

- [ ] Acrescentar secoes Spectrum identificadas nos documentos originais
  pertinentes: instalacao, linguagem, ferramentas e novos modulos.
- [ ] Acrescentar links/indicacoes no README sem apagar o texto MSX/CoCo.
- [ ] Se necessario, criar referencia especifica `documentation/ZX_SPECTRUM.md`,
  ligada aos manuais existentes, sem substitui-los.
- [ ] Documentar limites, sintaxe, exemplos, configuracao EightyOne e TAP/TZX.
- [ ] Adicionar sintaxes/snippets/tasks VS Code e Sublime em entrega separada,
  sem tornar esses editores obrigatorios para a CLI.
- [ ] Comparar os documentos com a base: cada linha original deve continuar
  presente na mesma ordem; apenas inserir material novo.
- [ ] Atualizar versao/changelog quando houver funcionalidade implementada,
  nao nesta analise, e preparar revisao independente do trabalho ZX81.

Aceite: texto original do Farique preservado e novas instrucoes refletem
o comportamento efetivamente verificado.

## 9. Matriz minima de verificacao futura

| Area | Casos que precisam passar |
| --- | --- |
| Fluxo Dignified | DEFINE com argumentos, INCLUDE, DECLARE, FUNC/RET, labels, loop/EXIT |
| Controle | GO TO/GO SUB, alias sem espaco, THEN com salto, destino inexistente |
| Nomes | Escalar longo, snake_case, string, FOR/NEXT, DIM, conflitos, esgotamento |
| Literais | Aspas duplicadas, apostrofo PRINT, REM com `:`/digitos/palavras-chave |
| Expressoes | DATA com expressao/variavel/macro, BIN, TO/slicing, booleanos |
| FN nativa | Sem/com parametros, parametros ocultos e escopo, execucao na ROM |
| Numeros | 0, 1, 255, 256, 65535, 65536, sinal, 0.1, expoente, limites/erro |
| Linha | Endianness, comprimento incluindo CR, ultima linha, longa, ordem, repeticao |
| Numeracao | Inicio/passo, zero, 9999, overflow depois do cabecalho/includes |
| TAP | Tipo BASIC, nome 10 bytes, tamanho, XOR, autorun e offset de variaveis |
| TZX | Assinatura, versao, pausa, blocos 0x10, payload igual ao TAP |
| Interfaces | INI/CLI/remtags, `-asc`, `-ss`, formatos ambos, caminhos com espacos |
| Erros | Entrada invalida nao inicia emulador nem aparenta gerar artefato valido |
| Regressao | MSX/CoCo, seus defaults, relatorios e geracao inalterados |
| Emulacao | LOAD e LIST, RUN, cores/som/dados/FN, TAP e TZX no EightyOne |

Nao ha testes Spectrum executados nesta analise e nao foi afirmado que
programas Spectrum ja carregam. A validacao atual e estatica/documental.

## 10. Referencias consultadas

Codigo e arquitetura:

- [Visao original de novos modulos](documentation/NEW_MODULES.md).
- [Configuracao e importacao dinamica](support/badig_settings.py#L68).
- [Linguagem MSX](msx/badig_msx.py).
- [Linguagem CoCo](coco/badig_coco.py).
- [Pipeline principal](badig.py).
- [Ferramentas originais](documentation/MODULE_TOOLS.md).
- Branch `suporte-zx81`: diff de `badig.py` e
  `support/badig_settings.py`, descricao/tokenizer/interfaces ZX81.

Referencias publicas, consultadas em 2026-11-04:

- [Manual Sinclair: programacao e linhas](https://worldofspectrum.org/ZXBasicManual/zxmanchap2.html).
- [Manual: nomes, numeros e aspas](https://worldofspectrum.org/ZXBasicManual/zxmanchap7.html).
- [Manual: slicing de strings](https://worldofspectrum.org/ZXBasicManual/zxmanchap8.html).
- [Manual: funcoes e DEF FN](https://worldofspectrum.org/ZXBasicManual/zxmanchap9.html).
- [Manual: caracteres, graficos e BIN](https://worldofspectrum.org/ZXBasicManual/zxmanchap14.html).
- [Manual: fitas e SAVE LINE](https://worldofspectrum.org/ZXBasicManual/zxmanchap20.html).
- [Manual: memoria e representacao numerica](https://worldofspectrum.org/ZXBasicManual/zxmanchap24.html).
- [Manual: referencia de tipos e comandos](https://worldofspectrum.org/ZXBasicManual/zxmanappc.html).
- [FAQ: formatos, incluindo TAP](https://worldofspectrum.org/faq/reference/formats.htm).
- [TZX 1.20, assinatura e bloco 0x10](https://worldofspectrum.net/TZXformat.html).
- [Projeto EightyOne e suporte Spectrum](https://sourceforge.net/projects/eightyone-sinclair-emulator/).

As referencias descrevem a plataforma; as hipoteses de CLI/automacao
EightyOne permanecem pendentes da prova pratica da etapa 0.
