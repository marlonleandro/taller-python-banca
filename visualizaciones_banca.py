import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Cargar datos
clientes = pd.read_csv("data/clientes.csv")
cartera = pd.read_csv("data/cartera_creditos.csv", parse_dates=["fecha_desembolso"])
pagos = pd.read_csv("data/pagos.csv", parse_dates=["fecha_pago"])

# Procesamiento equivalente al script original
cartera_activa = cartera[cartera["estado_credito"].isin(["Vigente", "Refinanciado"])].copy()
cartera_full = cartera_activa.merge(clientes, on="customer_id", how="left")

pagos_resumen = (
    pagos.groupby("loan_id", as_index=False)
         .agg(
            total_pagado=("monto_pagado", "sum"),
            n_pagos=("payment_id", "count"),
            ultimo_pago=("fecha_pago", "max")
         )
)

cartera_full = cartera_full.merge(pagos_resumen, on="loan_id", how="left")
cartera_full["total_pagado"] = cartera_full["total_pagado"].fillna(0)
cartera_full["n_pagos"] = cartera_full["n_pagos"].fillna(0)
cartera_full["en_mora"] = cartera_full["dias_mora"] > 0
cartera_full["mora_critica"] = cartera_full["dias_mora"] > 60
cartera_full["alto_esfuerzo_pago"] = cartera_full["ratio_cuota_ingreso"] > 0.35

# Preparar figura con 3 subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Análisis de Cartera Crediticia - Indicadores Bancarios Clave', 
             fontsize=16, fontweight='bold', y=0.995)

# ============================================================================
# GRÁFICO 1: Distribución de Cartera por Segmento
# ============================================================================
ax1 = axes[0, 0]

kpi_segmento = (
    cartera_full.groupby("segmento", as_index=False)
    .agg(
        creditos=("loan_id", "count"),
        saldo_total=("saldo_actual", "sum"),
        mora_rate=("en_mora", "mean")
    )
    .sort_values("saldo_total", ascending=True)
)

# Crear gráfico de barras horizontal con dos series
x_pos = np.arange(len(kpi_segmento))
width = 0.35

bars1 = ax1.barh(x_pos - width/2, kpi_segmento["creditos"], width, 
                 label='Cantidad de Créditos', color='#2E86AB', alpha=0.8)
ax1_twin = ax1.twiny()
bars2 = ax1_twin.barh(x_pos + width/2, kpi_segmento["saldo_total"]/1_000_000, width, 
                      label='Saldo Total (M$)', color='#A23B72', alpha=0.8)

ax1.set_yticks(x_pos)
ax1.set_yticklabels(kpi_segmento["segmento"])
ax1.set_xlabel('Cantidad de Créditos', fontsize=11, fontweight='bold')
ax1_twin.set_xlabel('Saldo Total (Millones $)', fontsize=11, fontweight='bold', color='#A23B72')
ax1_twin.tick_params(axis='x', labelcolor='#A23B72')
ax1.set_title('1. Distribución de Cartera por Segmento', fontsize=12, fontweight='bold', pad=10)
ax1.grid(axis='x', alpha=0.3)

# Combinar leyendas
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='lower right', framealpha=0.95)

# ============================================================================
# GRÁFICO 2: Tasa de Mora y Provision por Segmento y Región
# ============================================================================
ax2 = axes[0, 1]

kpi_segmento_region = (
    cartera_full.groupby(["segmento", "region"], as_index=False)
    .agg(
        creditos=("loan_id", "count"),
        saldo_total=("saldo_actual", "sum"),
        mora_rate=("en_mora", "mean"),
        provision_total=("provision", "sum")
    )
    .sort_values("mora_rate", ascending=False)
)

# Scatter plot: Mora Rate vs Saldo Total, coloreado por provisión
scatter = ax2.scatter(kpi_segmento_region["saldo_total"]/1_000_000, 
                     kpi_segmento_region["mora_rate"]*100,
                     s=kpi_segmento_region["provision_total"]/1000,  # Tamaño por provisión
                     c=kpi_segmento_region["creditos"],  # Color por cantidad de créditos
                     cmap='YlOrRd', alpha=0.6, edgecolors='black', linewidth=1.5)

ax2.axhline(y=8, color='red', linestyle='--', linewidth=2, label='Umbral Alerta (8%)', alpha=0.7)
ax2.set_xlabel('Saldo Total (Millones $)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Tasa de Mora (%)', fontsize=11, fontweight='bold')
ax2.set_title('2. Focos de Riesgo: Mora vs Saldo por Región/Segmento', fontsize=12, fontweight='bold', pad=10)
ax2.grid(alpha=0.3)
ax2.legend(loc='upper right', framealpha=0.95)

cbar = plt.colorbar(scatter, ax=ax2)
cbar.set_label('Cantidad de Créditos', fontsize=10, fontweight='bold')

# Añadir etiquetas a puntos críticos
alertas = kpi_segmento_region[kpi_segmento_region["mora_rate"] > 0.08]
for idx, row in alertas.head(3).iterrows():
    ax2.annotate(f'{row["segmento"]}/{row["region"]}', 
                xy=(row["saldo_total"]/1_000_000, row["mora_rate"]*100),
                xytext=(5, 5), textcoords='offset points', fontsize=8,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', lw=0.5))

# ============================================================================
# GRÁFICO 3: Relación entre Esfuerzo de Pago y Mora
# ============================================================================
ax3 = axes[1, 0]

# Crear bins para ratio de cuota/ingreso y calcular mora en cada bin
cartera_full['esfuerzo_bin'] = pd.cut(cartera_full['ratio_cuota_ingreso'], 
                                       bins=[0, 0.20, 0.35, 0.50, 1.0],
                                       labels=['Bajo\n(0-20%)', 'Moderado\n(20-35%)', 
                                              'Alto\n(35-50%)', 'Crítico\n(>50%)'])

relacion_esfuerzo = (
    cartera_full.groupby('esfuerzo_bin', observed=True, as_index=False)
    .agg(
        cantidad_clientes=('customer_id', 'count'),
        mora_rate=('en_mora', 'mean'),
        mora_critica_rate=('mora_critica', 'mean')
    )
)

x_pos = np.arange(len(relacion_esfuerzo))
width = 0.35

bars1 = ax3.bar(x_pos - width/2, relacion_esfuerzo['mora_rate']*100, width, 
               label='Mora General', color='#F18F01', alpha=0.8)
bars2 = ax3.bar(x_pos + width/2, relacion_esfuerzo['mora_critica_rate']*100, width, 
               label='Mora Crítica (>60d)', color='#C1121F', alpha=0.8)

ax3.set_xlabel('Nivel de Esfuerzo de Pago (Cuota/Ingreso)', fontsize=11, fontweight='bold')
ax3.set_ylabel('Tasa de Mora (%)', fontsize=11, fontweight='bold')
ax3.set_title('3. Impacto del Esfuerzo de Pago en la Mora', fontsize=12, fontweight='bold', pad=10)
ax3.set_xticks(x_pos)
ax3.set_xticklabels(relacion_esfuerzo['esfuerzo_bin'])
ax3.legend(loc='upper left', framealpha=0.95)
ax3.grid(axis='y', alpha=0.3)

# Añadir valores encima de barras
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

# ============================================================================
# GRÁFICO 4: Estadísticas Generales y Métricas Clave
# ============================================================================
ax4 = axes[1, 1]
ax4.axis('off')

# Calcular métricas generales
total_creditos = len(cartera_full)
saldo_total = cartera_full["saldo_actual"].sum()
mora_rate = cartera_full["en_mora"].mean()
mora_critica_rate = cartera_full["mora_critica"].mean()
provision_total = cartera_full["provision"].sum()
cobertura_provision = provision_total / saldo_total if saldo_total > 0 else 0
alto_esfuerzo_rate = cartera_full["alto_esfuerzo_pago"].mean()

# Crear tabla de indicadores
text_content = f"""
╔══════════════════════════════════════════════════════════════════╗
║               INDICADORES PRINCIPALES DE LA CARTERA              ║
╚══════════════════════════════════════════════════════════════════╝

📊 VOLUMEN DE CARTERA
   • Total de Créditos Activos:     {total_creditos:,}
   • Saldo Total:                   ${saldo_total:,.0f}
   • Ticket Promedio:               ${saldo_total/total_creditos:,.0f}

⚠️  INDICADORES DE RIESGO
   • Tasa de Mora General:          {mora_rate:.2%}
   • Tasa de Mora Crítica (>60d):   {mora_critica_rate:.2%}
   • Clientes en Alto Esfuerzo:     {alto_esfuerzo_rate:.2%}

🛡️  COBERTURA Y PROVISIONES
   • Provisión Total:               ${provision_total:,.0f}
   • Ratio de Cobertura:            {cobertura_provision:.2%}
   
📈 MEJORES PRACTICAS RECOMENDADAS
   ✓ Monitorear segmentos con mora > 10%
   ✓ Refinar políticas para alto esfuerzo
   ✓ Aumentar cobertura en regiones críticas
"""

ax4.text(0.05, 0.95, text_content, transform=ax4.transAxes, 
        fontsize=10, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#E8F4F8', alpha=0.8, pad=1))

# Ajustar espaciado entre subplots
plt.tight_layout()

# Guardar figura
plt.savefig('./images/graficos_analisis_banca.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Gráficos generados y guardados en 'graficos_analisis_banca.png'")

# Mostrar gráficos
plt.show()

print("\n" + "="*70)
print("EXPLICACIÓN DE LOS GRÁFICOS Y SU APLICACIÓN EN BANCA:")
print("="*70)
print("""
1️⃣  DISTRIBUCIÓN DE CARTERA POR SEGMENTO
    Utilidad: Identificar qué segmentos generan más volumen de créditos
    y qué saldo representan en la cartera total.
    Acción: Asignar recursos de supervisión proporcionales al riesgo
    y volumen de cada segmento.

2️⃣  FOCOS DE RIESGO: MORA vs SALDO
    Utilidad: Detectar combinaciones segmento-región con alto riesgo.
    El tamaño de la burbuja representa colateral (provisión).
    Acción: Priorizar intervenciones en focos con alta mora y alto saldo.

3️⃣  IMPACTO DEL ESFUERZO DE PAGO EN MORA
    Utilidad: Demostrar que clientes con cuotas altas respecto a su
    ingreso tienen mayores tasas de mora y mora crítica.
    Acción: Refinar políticas de originación para no exceder ratios
    de cuota/ingreso superiores a 35%.
""")
