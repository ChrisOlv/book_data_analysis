Points d’amélioration possibles

Performance

Beaucoup de groupby lourds sur des DataFrames potentiellement grands. Tu pourrais pré-calculer certaines métriques dans @st.cache_data pour éviter de recalculer à chaque interaction.

Certains groupby sont faits plusieurs fois pour les mêmes périodes (3 jours, 7 jours, 30 jours…) → tu peux factoriser dans une fonction.

Cohérence graphique

Les bar charts Plotly sont horizontaux, alors que tes line charts Matplotlib sont verticaux → tu peux harmoniser l’orientation et la palette de couleurs pour plus de cohérence.

L’usage mixte Plotly et Matplotlib peut rendre le style moins homogène. Tu pourrais migrer toutes les visualisations interactives vers Plotly pour la cohérence et l’interactivité.

Lecture par heure du jour

Tu as fait un KDE avec Seaborn pour la densité → tu pourrais aussi le faire en Plotly px.histogram avec histnorm='probability density' pour interactivité et hover.

Annotations line chart

Les offsets aléatoires (offset_x, offset_y) sont un peu chaotiques. On pourrait mieux gérer la position pour éviter que le texte se chevauche.

Matrice / KPIs

Les valeurs de la matrice sont converties en int → perte de précision. Peut-être arrondir à 1 décimale pour temps et vitesse.

Heatmap

Actuellement fixe avec plt et calmap. Si tu veux de l’interactivité, tu peux remplacer par Plotly px.imshow ou px.density_heatmap avec hover