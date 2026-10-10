# 02 — Detecção de conflitos de controle, blocos básicos e borda

**What to build:** como estudante, vejo no console os conflitos de controle com cada desvio e seu ocupante do slot, os blocos básicos do programa e os conflitos de dados que atravessam a fronteira do desvio nos dois caminhos possíveis.

**Blocked by:** 01 — Endereçamento sequencial e detecção de conflitos de dados.

**Status:** ready-for-agent

- [ ] Cada desvio condicional mostra o ocupante do slot de atraso; slot sempre executado seja o desvio tomado ou não
- [ ] Blocos básicos delimitados onde todo alvo de desvio ou salto inicia um bloco e todo desvio ou salto encerra um
- [ ] Conflitos de borda detectados entre produtor anterior ao desvio e consumidor no início de cada um dos dois caminhos, com endereço, registrador e distância
- [ ] Saída de controle separada da de dados no formato canônico; inválidas não viram bloco nem slot
- [ ] Código segue o subconjunto simples sem tipagem, sem operadores binários e sem importações novas além de módulos locais
