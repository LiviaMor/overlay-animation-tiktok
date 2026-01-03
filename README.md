# 🎬 TikTok Live Overlay

Overlay animado para lives do TikTok que exibe o avatar e nome de usuário de cada pessoa que entra na sua transmissão.

![Preview](https://img.shields.io/badge/TikTok-Live-ff0050?style=for-the-badge&logo=tiktok)

## ✨ Funcionalidades

- 🎉 **Notificação de entrada** - Mostra avatar + username quando alguém entra na live
- 🎨 **Animação fade-in** - Transição suave e profissional
- ⏱️ **Fila inteligente** - Se várias pessoas entrarem ao mesmo tempo, mostra uma por uma
- 🔧 **Personalizável** - Tamanho do avatar, tempo de exibição, cores e mensagens
- ☁️ **Deploy na nuvem** - Funciona 24/7 sem precisar deixar o computador ligado
- 🔗 **URL pública** - Compatível com TikTok Live Studio

## 🚀 Deploy no Render (Gratuito)

### Passo 1: Criar conta no Render

1. Acesse [render.com](https://render.com)
2. Clique em **Get Started for Free**
3. Faça login com sua conta do **GitHub**

### Passo 2: Criar o Web Service

1. No dashboard, clique em **New +** → **Web Service**
2. Conecte seu repositório GitHub (ou use este: `LiviaMor/overlay-animation-tiktok`)
3. Configure:
   - **Name**: `tiktok-overlay` (ou outro nome)
   - **Region**: Escolha a mais próxima
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

4. Clique em **Create Web Service**

### Passo 3: Configurar variável de ambiente

1. No seu serviço, vá em **Environment** (menu lateral)
2. Clique em **Add Environment Variable**
3. Adicione:
   - **Key**: `TIKTOK_USERNAME`
   - **Value**: `seu_usuario` (seu @ do TikTok, sem o @)
4. Clique em **Save Changes**

### Passo 4: Usar no TikTok Live Studio

1. Copie a URL do seu serviço (ex: `https://tiktok-overlay.onrender.com`)
2. Adicione `/overlay` no final: `https://tiktok-overlay.onrender.com/overlay`
3. No TikTok Live Studio:
   - Clique em **Adicionar Fonte**
   - Escolha **Link da Web** ou **Navegador**
   - Cole a URL completa
   - Ajuste o tamanho e posição na tela

## ⚙️ Personalização

Edite o arquivo `templates/index.html` para customizar:

```css
:root {
    /* Tamanho do avatar em pixels */
    --avatar-size: 300px;
    
    /* Duração da animação de fade-in */
    --fade-duration: 0.8s;
    
    /* Tempo que fica na tela (milissegundos) */
    --display-time: 5000;
}
```

### Mensagens

No HTML, você pode alterar as mensagens:
- `Bem-vindo à live! 🎉` - Mensagem de boas-vindas
- `acabou de entrar! 💜` - Texto após o username

## 🧪 Testando

Acesse `/test` para simular uma entrada:
```
https://sua-url.onrender.com/test
```

## 📁 Estrutura do Projeto

```
├── app.py              # Servidor Flask + TikTokLive
├── requirements.txt    # Dependências Python
├── render.yaml         # Configuração do Render
├── Dockerfile          # Para rodar via Docker
└── templates/
    └── index.html      # Visual do overlay
```

## 🔧 Rodar Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar usuário (opcional, padrão: aliviamor)
export TIKTOK_USERNAME=seu_usuario

# Rodar
python app.py
```

Acesse: `http://localhost:5000/overlay`

## 📝 Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `TIKTOK_USERNAME` | Seu @ do TikTok (sem @) | `aliviamor` |
| `PORT` | Porta do servidor | `5000` |

## ⚠️ Observações

- O usuário precisa estar **em live** para o overlay funcionar
- O plano gratuito do Render pode ter **cold starts** (demora ~30s para acordar se ficar inativo)
- Lives com restrição de idade podem não funcionar

## 📄 Licença

MIT License - Use à vontade!

---

Feito com 💜 para streamers do TikTok
