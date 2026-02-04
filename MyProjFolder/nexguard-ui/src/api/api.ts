const API_BASE = 'http://nexguard-fraud-alb-123456.us-east-1.elb.amazonaws.com';

export const fetchFraudData = async () => {
  const res = await fetch(`${API_BASE}/fraud`);
  if (!res.ok) throw new Error('Failed to fetch fraud data');
  return res.json();
};

export const fetchChurnData = async () => {
  const res = await fetch(`${API_BASE}/churn`);
  if (!res.ok) throw new Error('Failed to fetch churn data');
  return res.json();
};
