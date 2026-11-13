# Direct Tailscale serving

User explicitly requested binding to 0.0.0.0 for direct Tailscale access.
Changed only plantwise-staging.service and its checked-in template from
127.0.0.1 to 0.0.0.0:8175. Reloaded user units and restarted our staging service.
Host Tailscale IPv4: 100.82.28.38. Verified health, frontend and a real
recommendation query through http://100.82.28.38:8175 (20 results).
Model release unchanged: full_20261111T1252Z, 268 models.
No DNS/cloudflared or other services changed.
