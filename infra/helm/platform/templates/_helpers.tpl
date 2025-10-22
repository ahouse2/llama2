{{- define "discovery-platform.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "discovery-platform.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "discovery-platform.chart" -}}
{{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "discovery-platform.selectorLabels" -}}
{{- $ctx := index . "context" -}}
{{- $component := index . "component" | default "" -}}
app.kubernetes.io/name: {{ include "discovery-platform.name" $ctx }}
app.kubernetes.io/instance: {{ $ctx.Release.Name }}
{{- if $component }}
app.kubernetes.io/component: {{ $component }}
{{- end -}}
{{- end -}}

{{- define "discovery-platform.labels" -}}
{{- $ctx := index . "context" -}}
{{- $component := index . "component" | default "" -}}
helm.sh/chart: {{ include "discovery-platform.chart" $ctx }}
app.kubernetes.io/managed-by: {{ $ctx.Release.Service }}
{{ include "discovery-platform.selectorLabels" (dict "context" $ctx "component" $component) }}
{{- end -}}

{{- define "discovery-platform.otelHeaders" -}}
{{- $headers := index . "headers" -}}
{{- $pairs := list -}}
{{- range $key, $value := $headers }}
{{- $pairs = append $pairs (printf "%s=%s" $key $value) -}}
{{- end -}}
{{- join $pairs "," -}}
{{- end -}}

{{- define "discovery-platform.resourceAttributes" -}}
{{- $ctx := index . "context" -}}
{{- $component := index . "component" -}}
{{- $pairs := list -}}
{{- $ns := default $ctx.Release.Namespace $ctx.Values.namespace.name -}}
{{- range $key, $value := $ctx.Values.global.otel.resourceAttributes }}
{{- $pairs = append $pairs (printf "%s=%s" $key $value) -}}
{{- end -}}
{{- $pairs = append $pairs (printf "service.name=%s-%s" (include "discovery-platform.name" $ctx) $component) -}}
{{- $pairs = append $pairs (printf "service.instance.id=%s" $ctx.Release.Revision) -}}
{{- $pairs = append $pairs (printf "kubernetes.namespace=%s" $ns) -}}
{{- join $pairs "," -}}
{{- end -}}
