const express = require("express");
const { exec } = require("child_process");
const cors = require("cors");
const path = require("path");
const { Octokit } = require("@octokit/rest");
require("dotenv").config();

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 5000;

// Serve frontend
app.use(express.static(path.join(__dirname, "public")));

// GitHub Pull Request Diff Endpoint
app.get("/pulls", async (req, res) => {
    const { owner, repo, pull_number } = req.query;

    if (!process.env.GITHUB_TOKEN) {
        return res.status(500).json({ error: "GitHub token not configured" });
    }

    const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

    try {
        const { data: diff } = await octokit.request(
            `GET /repos/${owner}/${repo}/pulls/${pull_number}`, {
                mediaType: {
                    format: 'diff'
                }
            }
        );

        res.json({
            diff: diff,
            message: `Successfully fetched diff for ${owner}/${repo}#${pull_number}`
        });

    } catch (error) {
        console.error("GitHub API Error:", error);
        res.status(500).json({
            error: "Failed to fetch pull request",
            details: error.message
        });
    }
});

// Start Server
app.listen(PORT, () => {
    console.log(`✅ Server running at: http://localhost:${PORT}`);
});
