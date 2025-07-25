export interface User {
  id: string;
  email: string;
  full_name: string;
  phone_number?: string;
  date_of_birth?: string;
  age_range?: string;
  allergies: string[];
  medical_conditions: string[];
  is_verified: boolean;
  created_at: string;
  last_login_at?: string;
}

export interface Medication {
  id: string;
  generic_name: string;
  brand_names: string[];
  dosage_form: string;
  strength: string;
  route_of_administration: string[];
  prescription_required: boolean;
  indications: string[];
  warnings: string[];
  manufacturer: string;
  data_source: string;
  rxcui?: string;
}

export interface UserMedication {
  id: string;
  medication_id: string;
  medication_name: string;
  brand_names: string[];
  prescribed_by?: string;
  dosage_prescribed?: string;
  user_notes?: string;
  is_currently_taking: boolean;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  mentioned_medications?: string[];
  risk_level?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  phone_number?: string;
  date_of_birth?: string;
}
