import React, { useState } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Bike, Lock, Mail, User, Hash } from 'lucide-react';

export const AuthPage: React.FC = () => {
  const { login } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({
    mssv: '',
    email: '',
    full_name: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      if (isLogin) {
        const res = await api.post('/api/auth/login', {
          email: form.email,
          password: form.password,
        });
        await login(res.data.access_token, res.data.user);
      } else {
        const res = await api.post('/api/auth/register', {
          ...form,
          role: 'STUDENT',
        });
        await login(res.data.access_token, res.data.user);
      }
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(detail.map((d: any) => d.msg).join(', '));
      } else if (!err.response) {
        setError('Không thể kết nối đến máy chủ. Vui lòng kiểm tra Backend.');
      } else {
        setError('Đã xảy ra lỗi xác thực.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-blue-600 p-6 text-white text-center">
          <div className="inline-flex p-3 bg-white/20 rounded-full mb-3">
            <Bike className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold">Smart E-Mobility Hub</h1>
          <p className="text-blue-100 text-sm mt-1">Hệ thống điều phối xe điện ĐHQG-HCM</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="flex border-b pb-2 mb-4">
            <button
              type="button"
              onClick={() => {
                setIsLogin(true);
                setError('');
              }}
              className={`flex-1 py-2 font-semibold text-sm ${
                isLogin ? 'text-blue-600 border-b-2 border-blue-600' : 'text-slate-400'
              }`}
            >
              Đăng nhập
            </button>
            <button
              type="button"
              onClick={() => {
                setIsLogin(false);
                setError('');
              }}
              className={`flex-1 py-2 font-semibold text-sm ${
                !isLogin ? 'text-blue-600 border-b-2 border-blue-600' : 'text-slate-400'
              }`}
            >
              Đăng ký tài khoản
            </button>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg">
              {error}
            </div>
          )}

          {!isLogin && (
            <>
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Mã số SV / Nhân viên</label>
                <div className="relative">
                  <Hash className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    required
                    placeholder="VD: 2410709"
                    className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                    value={form.mssv}
                    onChange={(e) => setForm({ ...form, mssv: e.target.value })}
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Họ và tên</label>
                <div className="relative">
                  <User className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    required
                    placeholder="Nguyễn Văn A"
                    className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                    value={form.full_name}
                    onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  />
                </div>
              </div>
            </>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Email ĐHQG-HCM</label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
              <input
                type="email"
                required
                placeholder="name@hcmut.edu.vn"
                className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Mật khẩu (Tối thiểu 8 ký tự)</label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
              <input
                type="password"
                required
                minLength={8}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg text-sm transition disabled:opacity-50"
          >
            {submitting ? 'Đang xử lý...' : isLogin ? 'Đăng nhập vào hệ thống' : 'Tạo tài khoản & Nhận 150,000₫'}
          </button>
        </form>
      </div>
    </div>
  );
};