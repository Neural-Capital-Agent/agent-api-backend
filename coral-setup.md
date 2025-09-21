# Coral Protocol Setup Guide for Neural Capital Agents

## 1. Wallet Setup

### Step 1: Run Interactive Keygen
Execute the following command to set up your Coral Protocol wallet:

```bash
./gradlew run --args="--interactive-keygen-crossmint"
```

### Step 2: Enter Crossmint API Key
When prompted, enter your Crossmint API key:
```
c2tfcHJvZHVjdGlvbl81ajJNS3IzWDk5U3lwSHJoWEtuU21meFBUMXlBc3E5R0JQaGh5aHlLdUNMYmZiSEdEVmV2clJSakc4VWFrdnhiQ1lCajVxNWpjbW9NSjIzNVQ1Z2drWng5a2tiQTlLczM0bURxMkhxbzFYWGZQNEFHbmZVYW9BR29hUnFwam0yTHRmenFkVHF3SmFVR3pZbzZtWUxYZnVFbkFNOWJwcEZEQk5mQUdpamhCNDFidzlFMTRydGE3RUdIYkFNdXQ5YXlTNHRORE56ZnI0UTRQcjRuejFFYlBaTVAK
```

### Step 3: Complete Authentication
Follow the authentication URL that will be provided and enter:
- Your wallet public address from the sign-in page
- Your Crossmint affiliated email

## 2. Expected Files After Setup

After completing the wallet setup, you should find these files in `~/.coral/`:
- `wallet.toml` - Wallet configuration
- `crossmint-keypair.json` - Crossmint key pair
- `registry` - Local agent registry

## 3. Next Steps

1. Configure your agents with `coral-agent.toml` files
2. Build Docker images for each agent
3. Set up export settings and pricing
4. Submit to marketplace at hello@coralprotocol.org

## 4. Beta Registration

Make sure you're signed up for the beta program:
https://docs.google.com/forms/d/e/1FAIpQLScrdR4Yf7C-LcAV1CGkCd1AMNIjj7CRlnAICUII4iYFkflN7w/viewform