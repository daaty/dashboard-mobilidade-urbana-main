import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Users, Target, DollarSign, BarChart3 } from 'lucide-react';

const MetasKPIs = ({ kpisData }) => {
  const kpis = [
    {
      title: "Penetração de Mercado",
      value: kpisData?.penetracao_mercado || "2.3%",
      meta: "10%",
      publico_alvo: kpisData?.publico_alvo_total || "14.045",
      cidade: kpisData?.cidade_destaque || "Colíder",
      icon: Target,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      trend: "up"
    },
    {
      title: "CAC por Motorista", 
      value: kpisData?.cac_motorista || "R$ 400",
      budget: "R$ 350",
      variacao: kpisData?.variacao_cac || "+14%",
      icon: Users,
      color: "text-green-600",
      bgColor: "bg-green-50",
      trend: "down"
    },
    {
      title: "ROI Campanhas",
      value: kpisData?.roi_medio || "250%",
      receita_gerada: kpisData?.receita_total || "R$ 12.500",
      investimento: kpisData?.investimento_total || "R$ 5.000",
      icon: DollarSign,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
      trend: "up"
    },
    {
      title: "Progressão Mensal",
      mes_atual: kpisData?.mes_atual || "2º Mês",
      meta_atual: kpisData?.meta_atual || "1%", 
      realizado: kpisData?.realizado || "1.2%",
      status: kpisData?.status || "acima da meta",
      icon: BarChart3,
      color: "text-indigo-600",
      bgColor: "bg-indigo-50",
      trend: "up"
    }
  ];

  const renderTrendIcon = (trend) => {
    return trend === 'up' ? (
      <TrendingUp className="h-4 w-4 text-green-500" />
    ) : (
      <TrendingDown className="h-4 w-4 text-red-500" />
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {kpis.map((kpi, index) => {
        const IconComponent = kpi.icon;
        
        return (
          <Card key={index} className="relative overflow-hidden">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {kpi.title}
              </CardTitle>
              <div className={`p-2 rounded-lg ${kpi.bgColor}`}>
                <IconComponent className={`h-4 w-4 ${kpi.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="text-2xl font-bold text-gray-900">
                    {kpi.value}
                  </div>
                  {renderTrendIcon(kpi.trend)}
                </div>
                
                {/* Informações específicas por KPI */}
                {kpi.title === "Penetração de Mercado" && (
                  <div className="space-y-1">
                    <div className="text-sm text-gray-500">
                      Meta: <span className="font-semibold">{kpi.meta}</span>
                    </div>
                    <div className="text-sm text-gray-500">
                      Público-alvo: <span className="font-semibold">{kpi.publico_alvo}</span>
                    </div>
                    <div className="text-sm text-gray-500">
                      Cidade destaque: <span className="font-semibold">{kpi.cidade}</span>
                    </div>
                  </div>
                )}

                {kpi.title === "CAC por Motorista" && (
                  <div className="space-y-1">
                    <div className="text-sm text-gray-500">
                      Budget: <span className="font-semibold">{kpi.budget}</span>
                    </div>
                    <div className="text-sm text-gray-500">
                      Variação: <span className="font-semibold text-red-600">{kpi.variacao}</span>
                    </div>
                  </div>
                )}

                {kpi.title === "ROI Campanhas" && (
                  <div className="space-y-1">
                    <div className="text-sm text-gray-500">
                      Receita: <span className="font-semibold">{kpi.receita_gerada}</span>
                    </div>
                    <div className="text-sm text-gray-500">
                      Investimento: <span className="font-semibold">{kpi.investimento}</span>
                    </div>
                  </div>
                )}

                {kpi.title === "Progressão Mensal" && (
                  <div className="space-y-1">
                    <div className="text-sm text-gray-500">
                      {kpi.mes_atual} - Meta: <span className="font-semibold">{kpi.meta_atual}</span>
                    </div>
                    <div className="text-sm text-gray-500">
                      Realizado: <span className="font-semibold text-green-600">{kpi.realizado}</span>
                    </div>
                    <div className="text-sm text-green-600 font-semibold">
                      {kpi.status}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};

export default MetasKPIs;
