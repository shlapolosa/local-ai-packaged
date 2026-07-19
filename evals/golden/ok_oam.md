## ✅ OAM generated — **acme-billing** (v7, intent: `oam`)

```yaml
apiVersion: core.oam.dev/v1beta1
kind: Application
metadata: {name: acme-billing-app, namespace: default}
spec:
  components:
    - name: acme-billing-api
      type: webservice
      properties: {image: nginx:1.25, port: 80}

```

<details><summary>🔬 Dry-run report (vela)</summary>

```
{"ok": true, "diagnostics": "Deployment rendered"}
```
</details>

_Mapped 1 capability(ies)._
_Agent used 6 turn(s)._
