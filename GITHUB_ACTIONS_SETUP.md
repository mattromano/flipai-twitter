# GitHub Actions Setup Guide

This guide will help you set up GitHub Actions to run your Flipside AI + Twitter automation workflow.

## 🔐 Required Repository Secrets

You need to add the following secrets to your GitHub repository:

### 1. Flipside Authentication
- **Secret Name:** `FLIPSIDE_COOKIES`
- **Value:** The base64-encoded cookies from your `flipside_cookies.txt` file
- **How to get it:** Copy the entire content of your `flipside_cookies.txt` file

- **Secret Name:** `FLIPSIDE_EMAIL`
- **Value:** Your Flipside Crypto login email
- **Purpose:** Used for automatic login fallback when cookies expire

- **Secret Name:** `FLIPSIDE_PASSWORD`
- **Value:** Your Flipside Crypto login password
- **Purpose:** Used for automatic login fallback when cookies expire

### 2. Twitter API Credentials
- **Secret Name:** `TWITTER_BEARER_TOKEN`
- **Value:** Your Twitter API Bearer Token

- **Secret Name:** `TWITTER_CONSUMER_KEY`
- **Value:** Your Twitter API Consumer Key

- **Secret Name:** `TWITTER_CONSUMER_SECRET`
- **Value:** Your Twitter API Consumer Secret

- **Secret Name:** `TWITTER_ACCESS_TOKEN`
- **Value:** Your Twitter API Access Token

- **Secret Name:** `TWITTER_ACCESS_TOKEN_SECRET`
- **Value:** Your Twitter API Access Token Secret

## 📋 How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with the exact name and value listed above

## 🚀 Workflow Features

### Automatic Scheduling
- Runs daily at 9 AM UTC
- Uses a default DeFi analysis prompt

### Manual Triggers
- Can be triggered manually from the GitHub Actions tab
- Supports custom prompts via the workflow dispatch interface

### Artifacts
- **Screenshots:** All captured screenshots and charts
- **Logs:** Analysis logs and Twitter post records
- **Results:** JSON analysis results and Twitter post data

### Summary Reports
- Detailed run summaries in GitHub Actions
- Statistics on files generated
- Latest Twitter post information

## 🔧 Workflow Configuration

The workflow is configured to:
- Use Python 3.11
- Run in headless mode (no GUI)
- Install all dependencies from `requirements.txt`
- Set up Chrome and ChromeDriver automatically
- Create the cookies file from the secret
- Run the full automation workflow
- Upload all generated files as artifacts

## 📊 Monitoring

After each run, you can:
1. View the workflow summary in the Actions tab
2. Download artifacts containing screenshots, logs, and results
3. Check the Twitter post logs for posting history
4. Monitor the automation logs for any issues

## 🛠️ Troubleshooting

### Common Issues

1. **Cookies not working:**
   - Ensure the `FLIPSIDE_COOKIES` secret contains the exact content from your `flipside_cookies.txt` file
   - Make sure there are no extra spaces or line breaks

2. **Twitter posting fails:**
   - Verify all Twitter API credentials are correctly set
   - Check that your Twitter app has "Read and Write" permissions
   - Ensure the access tokens are valid and not expired

3. **Chrome/ChromeDriver issues:**
   - The workflow automatically sets up Chrome and ChromeDriver
   - If issues persist, check the workflow logs for specific error messages

### Debug Mode

To enable debug mode for troubleshooting:
1. Go to the workflow file (`.github/workflows/daily-analysis.yml`)
2. Change `DEBUG_MODE: 'false'` to `DEBUG_MODE: 'true'`
3. Commit and push the changes

## 📝 Custom Prompts

To run with a custom prompt:
1. Go to the **Actions** tab in your repository
2. Click on **Flipside AI + Twitter Automation**
3. Click **Run workflow**
4. Enter your custom prompt in the input field
5. Click **Run workflow**

## 🔄 Updating Secrets

If you need to update any secrets:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Find the secret you want to update
3. Click **Update**
4. Enter the new value
5. Click **Update secret**

The next workflow run will use the updated secret.

## 📈 Workflow Performance

The workflow typically takes 5-10 minutes to complete:
- Setup: ~1-2 minutes
- Analysis: ~4-6 minutes
- Twitter posting: ~30 seconds
- Artifact upload: ~1-2 minutes

Total runtime depends on the complexity of the analysis and network conditions.
