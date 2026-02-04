// Fraud Detection Mock Data
export const fraudMetrics = {
  totalTransactions: 45280,
  fraudulentTransactions: 347,
  fraudRate: 0.77,
  riskScore: 68,
  previousFraudRate: 0.82,
}

export const fraudTrendData = [
  { date: 'Jan 1', frauds: 12, legitimate: 850 },
  { date: 'Jan 2', frauds: 15, legitimate: 920 },
  { date: 'Jan 3', frauds: 8, legitimate: 890 },
  { date: 'Jan 4', frauds: 22, legitimate: 950 },
  { date: 'Jan 5', frauds: 18, legitimate: 880 },
  { date: 'Jan 6', frauds: 25, legitimate: 1020 },
  { date: 'Jan 7', frauds: 10, legitimate: 900 },
  { date: 'Jan 8', frauds: 28, legitimate: 1100 },
  { date: 'Jan 9', frauds: 14, legitimate: 920 },
  { date: 'Jan 10', frauds: 32, legitimate: 1050 },
]

export const fraudByDeviceData = [
  { name: 'Desktop', value: 145, percentage: 42 },
  { name: 'Mobile', value: 120, percentage: 35 },
  { name: 'Tablet', value: 55, percentage: 16 },
  { name: 'Unknown', value: 27, percentage: 7 },
]

export const fraudByLocationData = [
  { location: 'California', frauds: 85, risk: 'high' },
  { location: 'New York', frauds: 62, risk: 'high' },
  { location: 'Texas', frauds: 48, risk: 'medium' },
  { location: 'Florida', frauds: 35, risk: 'medium' },
  { location: 'Illinois', frauds: 28, risk: 'low' },
  { location: 'Pennsylvania', frauds: 22, risk: 'low' },
  { location: 'Ohio', frauds: 18, risk: 'low' },
  { location: 'Others', frauds: 49, risk: 'medium' },
]

export const fraudAlerts = [
  {
    id: '1',
    type: 'velocity',
    message: 'Unusual transaction velocity detected',
    risk: 'high',
    timestamp: '5 minutes ago',
    accountId: 'ACC-2847',
  },
  {
    id: '2',
    type: 'geolocation',
    message: 'Login from new country detected',
    risk: 'high',
    timestamp: '12 minutes ago',
    accountId: 'ACC-5093',
  },
  {
    id: '3',
    type: 'mfa',
    message: 'Multiple MFA failures detected',
    risk: 'medium',
    timestamp: '28 minutes ago',
    accountId: 'ACC-1647',
  },
  {
    id: '4',
    type: 'chargeback',
    message: 'High chargeback ratio flagged',
    risk: 'medium',
    timestamp: '1 hour ago',
    accountId: 'ACC-3862',
  },
  {
    id: '5',
    type: 'device',
    message: 'Device fingerprint change detected',
    risk: 'low',
    timestamp: '2 hours ago',
    accountId: 'ACC-7421',
  },
]

// Churn Analysis Mock Data
export const churnMetrics = {
  totalCustomers: 12450,
  atRiskCustomers: 1247,
  churnedCustomers: 342,
  churnRate: 2.74,
  predictedChurn: 8.5,
  retentionRate: 97.26,
}

export const churnTrendData = [
  { month: 'Jan', churn: 42, retention: 9800 },
  { month: 'Feb', churn: 38, retention: 9950 },
  { month: 'Mar', churn: 55, retention: 9950 },
  { month: 'Apr', churn: 48, retention: 10050 },
  { month: 'May', churn: 65, retention: 9980 },
  { month: 'Jun', churn: 52, retention: 10120 },
  { month: 'Jul', churn: 47, retention: 10280 },
  { month: 'Aug', churn: 72, retention: 10150 },
  { month: 'Sep', churn: 58, retention: 10350 },
  { month: 'Oct', churn: 92, retention: 10280 },
  { month: 'Nov', churn: 78, retention: 10450 },
  { month: 'Dec', churn: 85, retention: 10420 },
]

export const churnRiskSegmentation = [
  { segment: 'High Risk', customers: 342, percentage: 27 },
  { segment: 'Medium Risk', customers: 528, percentage: 42 },
  { segment: 'Low Risk', customers: 377, percentage: 31 },
]

export const churnByReasonData = [
  { reason: 'Price Sensitivity', count: 145, percentage: 42 },
  { reason: 'Feature Gaps', count: 95, percentage: 28 },
  { reason: 'Poor Support', count: 62, percentage: 18 },
  { reason: 'Competitive Switch', count: 40, percentage: 12 },
]

export const customerSegmentData = [
  { segment: 'Enterprise', value: 3200 },
  { segment: 'Mid-Market', value: 4500 },
  { segment: 'SMB', value: 2800 },
  { segment: 'Startup', value: 1950 },
]

export const engagementScoreData = [
  { score: '90-100', customers: 2100 },
  { score: '75-89', customers: 3400 },
  { score: '60-74', customers: 4200 },
  { score: '45-59', customers: 1850 },
  { score: '0-44', customers: 900 },
]

export const rFMAnalysisData = [
  {
    segment: 'Champions',
    recency: 'Very Recent',
    frequency: 'High',
    monetary: 'High',
    customers: 1500,
    churnRisk: 'Very Low',
  },
  {
    segment: 'Loyal Customers',
    recency: 'Recent',
    frequency: 'High',
    monetary: 'Medium-High',
    customers: 2800,
    churnRisk: 'Low',
  },
  {
    segment: 'At-Risk',
    recency: 'Old',
    frequency: 'Medium',
    monetary: 'Medium',
    customers: 1900,
    churnRisk: 'High',
  },
  {
    segment: 'Lost',
    recency: 'Very Old',
    frequency: 'Low',
    monetary: 'Low',
    customers: 650,
    churnRisk: 'Very High',
  },
]

// Dashboard Overview Data
export const dashboardKPIs = [
  {
    title: 'Total Transactions',
    value: '45.2K',
    change: '+12.5%',
    trend: 'up',
    icon: 'TrendingUp',
  },
  {
    title: 'Fraud Detection Rate',
    value: '98.2%',
    change: '+2.3%',
    trend: 'up',
    icon: 'Shield',
  },
  {
    title: 'Active Customers',
    value: '12.4K',
    change: '-3.2%',
    trend: 'down',
    icon: 'Users',
  },
  {
    title: 'System Uptime',
    value: '99.98%',
    change: '+0.5%',
    trend: 'up',
    icon: 'Activity',
  },
]

export const recentActivity = [
  {
    id: '1',
    type: 'fraud_detected',
    description: 'High-risk transaction blocked',
    timestamp: '2 minutes ago',
    status: 'blocked',
  },
  {
    id: '2',
    type: 'customer_churned',
    description: 'Customer ABC Inc. marked as churned',
    timestamp: '15 minutes ago',
    status: 'churned',
  },
  {
    id: '3',
    type: 'alert_triggered',
    description: 'Multiple MFA failures from account XYZ',
    timestamp: '32 minutes ago',
    status: 'alert',
  },
  {
    id: '4',
    type: 'transaction_approved',
    description: 'Large transaction approved after review',
    timestamp: '1 hour ago',
    status: 'approved',
  },
]
