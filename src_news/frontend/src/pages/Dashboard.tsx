import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Bike, BatteryCharging, MapPin, LogOut, Wallet, RefreshCw } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user, wallet, ledger, logout, refreshProfile } = useAuth();
  const [activeTab, setActiveTab] = useState<'SS1' | 'SS2' | 'SS3' | 'SS4' | 'SS5' | 'SS67'>('SS1');
  const [hubs, setHubs] = useState<any[]>([]);
  const [bookings, setBookings] = useState<any[]>([]);
  const [chargingQueue, setChargingQueue] = useState<any[]>([]);
  const [personalData, setPersonalData] = useState<any>({ vehicles: [], reservations: [] });
  const [dispatches, setDispatches] = useState<any[]>([]);
  const [forecast, setForecast] = useState<any[]>([]);

  // SS1 states
  const [selectedHub, setSelectedHub] = useState('HUB-001');
  const [destHub, setDestHub] = useState('');
  const [selectedVehicle, setSelectedVehicle] = useState('');
  const [voucher, setVoucher] = useState('SVBK50');
  const [pinInput, setPinInput] = useState('');
  const [returnHub, setReturnHub] = useState('HUB-002');
  const [tripDuration, setTripDuration] = useState(25);
  const [altHubs, setAltHubs] = useState<any[]>([]);

  // SS2 states
  const [pevForm, setPevForm] = useState({ plate: '', type: 'scooter', brand: 'VinFast Klara S', battery_kwh: 3.5 });
  const [pevReserve, setPevReserve] = useState({ ev_id: '', hub_id: 'HUB-001', request_charging: true, current_soc: 35 });
  const [pevCheckout, setPevCheckout] = useState({ duration_hours: 2.0, kwh_charged: 3.5, overstay_minutes: 0 });
  const [lastPevInvoice, setLastPevInvoice] = useState<any>(null);

  // SS4 states
  const [dispForm, setDispForm] = useState({ source_hub_id: 'HUB-002', destination_hub_id: 'HUB-001', vehicle_ids: [] as string[], reason: 'Cân bằng tải giờ cao điểm' });
  const [incForm, setIncForm] = useState({ hub_id: 'HUB-001', target_type: 'VEHICLE', vehicle_id: '' });

  // SS5 & SS6/7 states
  const [allocHub, setAllocHub] = useState('HUB-001');
  const [surgeForm, setSurgeForm] = useState({ target_hub_id: 'HUB-002', num_new_students: 20 });
  const [surgePreview, setSurgePreview] = useState<any>(null);
  const [failForm, setFailForm] = useState({ target_hub_id: 'HUB-004', num_ports_down: 3 });
  const [failPreview, setFailPreview] = useState<any>(null);

  const [msg, setMsg] = useState<{ type: 'ok' | 'err'; text: string } | null>(null);
  const isOperator = user?.role === 'OPERATOR' || user?.role === 'ADMIN';

  const loadAllData = async () => {
    try {
      const [hubRes, bkRes, qRes, pevRes, dispRes] = await Promise.all([
        api.get('/api/hubs'),
        api.get('/api/bookings/my'),
        api.get('/api/operations/charging-queue'),
        api.get('/api/personal-ev/my'),
        api.get('/api/operations/dispatches'),
      ]);
      setHubs(hubRes.data);
      setBookings(bkRes.data);
      setChargingQueue(qRes.data);
      setPersonalData(pevRes.data);
      setDispatches(dispRes.data);
      if (isOperator) {
        const fcRes = await api.get('/api/hubs/forecast');
        setForecast(fcRes.data);
      }
      await refreshProfile();
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const notify = (type: 'ok' | 'err', text: string) => {
    setMsg({ type, text });
    setTimeout(() => setMsg(null), 5000);
  };

  // SS1 Handlers
  const handleBookVehicle = async () => {
    try {
      const res = await api.post('/api/bookings/create', {
        hub_id: selectedHub,
        vehicle_id: selectedVehicle,
        destination_hub_id: destHub || null,
        voucher_code: voucher || null,
      });
      notify('ok', `${res.data.message} Mã PIN: ${res.data.booking.pin_code}`);
      setPinInput(res.data.booking.pin_code);
      setSelectedVehicle('');
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi đặt xe');
    }
  };

  const handlePickup = async (bookingId: string) => {
    try {
      const res = await api.post('/api/bookings/pickup', { booking_id: bookingId, pin_code: pinInput });
      notify('ok', res.data.message);
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi nhận xe');
    }
  };

  const handleReturn = async (bookingId: string) => {
    try {
      const res = await api.post('/api/bookings/return', {
        booking_id: bookingId,
        return_hub_id: returnHub,
        duration_minutes: tripDuration,
      });
      notify('ok', `${res.data.message} Phí: ${res.data.invoice.final_fee.toLocaleString()}đ`);
      setAltHubs([]);
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi trả xe');
      const alts = await api.get(`/api/bookings/alternatives/${returnHub}`);
      setAltHubs(alts.data);
    }
  };

  const handleReroute = async (bookingId: string, newDestId: string) => {
    try {
      const res = await api.post('/api/bookings/reroute', { booking_id: bookingId, new_destination_hub_id: newDestId });
      notify('ok', res.data.message);
      setReturnHub(newDestId);
      setAltHubs([]);
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi điều hướng');
    }
  };

  const handleCancel = async (bookingId: string) => {
    try {
      const res = await api.post(`/api/bookings/cancel/${bookingId}`);
      notify('ok', res.data.message);
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi hủy đặt');
    }
  };

  // SS2 Handlers
  const handleRegisterPev = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/api/personal-ev/register', pevForm);
      notify('ok', res.data.message);
      setPevForm({ ...pevForm, plate: '' });
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi đăng ký xe');
    }
  };

  const handleReservePev = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/api/personal-ev/reserve', pevReserve);
      notify('ok', res.data.message);
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi đặt chỗ xe cá nhân');
    }
  };

  const handleCheckinPev = async (resId: string) => {
    try {
      const res = await api.post(`/api/personal-ev/checkin/${resId}`);
      notify('ok', res.data.message);
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi check-in');
    }
  };

  const handleCheckoutPev = async (resId: string) => {
    try {
      const res = await api.post('/api/personal-ev/checkout', { reservation_id: resId, ...pevCheckout });
      notify('ok', res.data.message);
      setLastPevInvoice(res.data.invoice);
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi check-out');
    }
  };

  // SS4 & SS5 Handlers
  const handleCreateDispatch = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/api/operations/dispatch', dispForm);
      notify('ok', res.data.message);
      setDispForm({ ...dispForm, vehicle_ids: [] });
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi tạo điều phối');
    }
  };

  const handleReceiveDispatch = async (dispId: string) => {
    try {
      const res = await api.post(`/api/operations/dispatch/${dispId}/receive`);
      notify('ok', res.data.message);
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi tiếp nhận xe');
    }
  };

  const handleIncidentAction = async (action: 'isolate' | 'recover') => {
    try {
      const res = await api.post(`/api/operations/incidents/${action}`, incForm);
      notify('ok', res.data.message);
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi xử lý sự cố');
    }
  };

  const handleAllocateCharging = async () => {
    try {
      const res = await api.post(`/api/operations/charging/allocate/${allocHub}`);
      notify('ok', res.data.message);
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi phân bổ cổng sạc');
    }
  };

  const handleUnplugCharging = async (vehicleId: string) => {
    try {
      const res = await api.post(`/api/operations/charging/unplug/${vehicleId}`);
      notify('ok', res.data.message);
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi rút sạc');
    }
  };

  const activeBooking = bookings.find((b) => b.status === 'RESERVED' || b.status === 'IN_USE');
  const currentHubObj = hubs.find((h) => h.hub_id === selectedHub);
  const availVehicles = (currentHubObj?.current_vehicles || []).filter((v: any) => v.status === 'AVAILABLE' && v.battery_soc >= 20);
  const srcDispHub = hubs.find((h) => h.hub_id === dispForm.source_hub_id);
  const dispVehicles = (srcDispHub?.current_vehicles || []).filter((v: any) => v.status === 'AVAILABLE');
  const incHubObj = hubs.find((h) => h.hub_id === incForm.hub_id);

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col justify-between p-4">
        <div>
          <div className="flex items-center gap-2 px-2 py-3 border-b border-slate-800">
            <Bike className="w-7 h-7 text-blue-400" />
            <div>
              <div className="font-bold text-sm">Smart E-Mobility</div>
              <div className="text-xs text-slate-400">ĐHQG-HCM • {user?.role}</div>
            </div>
          </div>

          <nav className="mt-6 space-y-1">
            {[
              { id: 'SS1', label: '1. Đặt xe dùng chung (SV)' },
              { id: 'SS2', label: '2. Xe điện cá nhân' },
              { id: 'SS3', label: '3. Giám sát Hub (Monitor)' },
              { id: 'SS4', label: '4. Điều phối & Sự cố' },
              { id: 'SS5', label: '5. Lập lịch sạc thông minh' },
              { id: 'SS67', label: '6-7. Mô phỏng What-if' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                  activeTab === tab.id ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="border-t border-slate-800 pt-4 space-y-3">
          <div className="bg-slate-800 p-3 rounded-lg text-xs space-y-1">
            <div className="font-semibold text-white">{user?.full_name} ({user?.mssv})</div>
            <div className="text-emerald-400 flex items-center gap-1">
              <Wallet className="w-3.5 h-3.5" /> Khả dụng: {wallet?.balance?.toLocaleString()} ₫
            </div>
            <div className="text-amber-400">Đang cọc: {wallet?.held_deposit?.toLocaleString()} ₫</div>
            {wallet?.debt > 0 && <div className="text-red-400">Dư nợ: {wallet?.debt?.toLocaleString()} ₫</div>}
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 py-2 bg-red-600/20 hover:bg-red-600 text-red-300 hover:text-white rounded-lg text-xs font-semibold transition"
          >
            <LogOut className="w-4 h-4" /> Đăng xuất
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-6 overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-slate-800">
            {activeTab === 'SS1' && '🚲 Quản lý & Đặt xe điện dùng chung (SS1)'}
            {activeTab === 'SS2' && '🔌 Dịch vụ Xe điện Cá nhân (SS2)'}
            {activeTab === 'SS3' && '📊 Giám sát Mạng lưới Trạm Hub (SS3)'}
            {activeTab === 'SS4' && '🚚 Điều phối Xe & Quản lý Sự cố Trạm (SS4)'}
            {activeTab === 'SS5' && '⚡ Hàng đợi Lập lịch Sạc Thông minh (SS5)'}
            {activeTab === 'SS67' && '🧪 Mô phỏng Kịch bản What-if (SS6 & SS7)'}
          </h2>
          <button onClick={loadAllData} className="flex items-center gap-1.5 px-3 py-1.5 bg-white border rounded-lg text-xs font-medium hover:bg-slate-50">
            <RefreshCw className="w-3.5 h-3.5" /> Làm mới dữ liệu
          </button>
        </div>

        {msg && (
          <div className={`p-4 mb-4 rounded-xl text-sm font-medium ${msg.type === 'ok' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
            {msg.text}
          </div>
        )}

        {/* SUBSYSTEM 1 */}
        {activeTab === 'SS1' && (
          <div className="space-y-6">
            {activeBooking ? (
              <div className="bg-white p-6 rounded-xl shadow-sm border border-blue-200 space-y-4">
                <div className="flex justify-between items-center">
                  <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-bold">
                    CHUYẾN ĐI HIỆN TẠI: {activeBooking.status}
                  </span>
                  <span className="text-xs text-slate-500">Mã: {activeBooking.booking_id}</span>
                </div>
                <p className="text-sm">
                  Xe: <strong>{activeBooking.vehicle_id}</strong> | Xuất phát: <strong>{activeBooking.hub_id}</strong> |
                  Đích giữ chỗ: <strong>{activeBooking.destination_hub_id || 'Chưa chọn'}</strong> |
                  PIN: <strong className="text-blue-600">{activeBooking.pin_code}</strong>
                  {activeBooking.extra_free_minutes > 0 && <span className="ml-2 text-emerald-600 font-semibold">(+{activeBooking.extra_free_minutes}p miễn phí điều hướng)</span>}
                </p>

                {activeBooking.status === 'RESERVED' && (
                  <div className="flex gap-3 items-center pt-2">
                    <input value={pinInput} onChange={(e) => setPinInput(e.target.value)} placeholder="Nhập PIN 4 số" className="border px-3 py-2 rounded-lg text-sm w-40" />
                    <button onClick={() => handlePickup(activeBooking.booking_id)} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-semibold">
                      🔓 Mở khóa & Nhận xe
                    </button>
                    <button onClick={() => handleCancel(activeBooking.booking_id)} className="px-4 py-2 bg-red-100 text-red-600 rounded-lg text-sm font-semibold">
                      Hủy đặt xe (Hoàn 100% cọc)
                    </button>
                  </div>
                )}

                {activeBooking.status === 'IN_USE' && (
                  <div className="space-y-3 pt-2">
                    <div className="flex flex-wrap gap-3 items-center">
                      <select value={returnHub} onChange={(e) => setReturnHub(e.target.value)} className="border px-3 py-2 rounded-lg text-sm">
                        {hubs.map((h) => (
                          <option key={h.hub_id} value={h.hub_id}>{h.name} (Trống {h.available_slots} chỗ)</option>
                        ))}
                      </select>
                      <input type="number" value={tripDuration} onChange={(e) => setTripDuration(Number(e.target.value))} className="border px-3 py-2 rounded-lg text-sm w-28" min={1} />
                      <span className="text-xs text-slate-500">phút di chuyển</span>
                      <button onClick={() => handleReturn(activeBooking.booking_id)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold">
                        ✅ Trả xe & Quyết toán
                      </button>
                    </div>
                    {altHubs.length > 0 && (
                      <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs space-y-2">
                        <div className="font-semibold text-amber-800">Hub đích đã đầy! Gợi ý điều hướng sang Hub lân cận (+15 phút miễn phí):</div>
                        {altHubs.map((a) => (
                          <div key={a.hub_id} className="flex items-center justify-between">
                            <span>{a.name} (~{a.distance_km} km • Còn {a.available_slots} chỗ)</span>
                            <button onClick={() => handleReroute(activeBooking.booking_id, a.hub_id)} className="px-3 py-1 bg-amber-600 text-white rounded font-semibold">
                              Chuyển sang trạm này
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
                <h3 className="font-semibold text-slate-800">Đặt giữ xe mới (Khóa cọc 50,000₫ • Miễn phí 30 phút đầu)</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-xs text-slate-500 mb-1">Hub xuất phát</label>
                    <select value={selectedHub} onChange={(e) => setSelectedHub(e.target.value)} className="w-full border p-2 rounded-lg text-sm">
                      {hubs.map((h) => <option key={h.hub_id} value={h.hub_id}>{h.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-slate-500 mb-1">Hub đích giữ chỗ trước</label>
                    <select value={destHub} onChange={(e) => setDestHub(e.target.value)} className="w-full border p-2 rounded-lg text-sm">
                      <option value="">-- Không giữ trước --</option>
                      {hubs.map((h) => <option key={h.hub_id} value={h.hub_id}>{h.name} ({h.available_slots} trống)</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-slate-500 mb-1">Chọn xe (Pin ≥ 20%)</label>
                    <select value={selectedVehicle} onChange={(e) => setSelectedVehicle(e.target.value)} className="w-full border p-2 rounded-lg text-sm">
                      <option value="">-- Chọn phương tiện --</option>
                      {availVehicles.map((v: any) => (
                        <option key={v.vehicle_id} value={v.vehicle_id}>{v.vehicle_id} ({v.type.toUpperCase()} - {v.battery_soc}%)</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-slate-500 mb-1">Mã Voucher (SVBK50 / VNU2026)</label>
                    <input value={voucher} onChange={(e) => setVoucher(e.target.value)} className="w-full border p-2 rounded-lg text-sm" />
                  </div>
                </div>
                <button disabled={!selectedVehicle} onClick={handleBookVehicle} className="px-5 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-semibold disabled:opacity-40">
                  Xác nhận đặt giữ xe (50,000₫)
                </button>
              </div>
            )}

            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <h3 className="font-semibold text-slate-800 mb-3">📜 Lịch sử biến động ví (Ledger)</h3>
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 border-b">
                  <tr>
                    <th className="p-2">Mã GD</th>
                    <th className="p-2">Loại</th>
                    <th className="p-2">Số tiền</th>
                    <th className="p-2">Số dư sau</th>
                    <th className="p-2">Ghi chú</th>
                  </tr>
                </thead>
                <tbody>
                  {ledger.map((tx: any) => (
                    <tr key={tx.tx_id} className="border-b">
                      <td className="p-2 font-mono">{tx.tx_id}</td>
                      <td className="p-2">{tx.tx_type}</td>
                      <td className={`p-2 font-semibold ${tx.amount >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                        {tx.amount >= 0 ? `+${tx.amount.toLocaleString()}` : tx.amount.toLocaleString()} ₫
                      </td>
                      <td className="p-2">{tx.balance_after.toLocaleString()} ₫</td>
                      <td className="p-2 text-slate-500">{tx.note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* SUBSYSTEM 2 */}
        {activeTab === 'SS2' && (
          <div className="space-y-6">
            <form onSubmit={handleRegisterPev} className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
              <h3 className="font-semibold text-slate-800">1. Đăng ký xe điện cá nhân mới</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <input required placeholder="Biển số (59-X1 888.88)" value={pevForm.plate} onChange={(e) => setPevForm({ ...pevForm, plate: e.target.value })} className="border p-2 rounded-lg text-sm" />
                <select value={pevForm.type} onChange={(e) => setPevForm({ ...pevForm, type: e.target.value })} className="border p-2 rounded-lg text-sm">
                  <option value="scooter">Scooter</option>
                  <option value="bike">Bike</option>
                  <option value="car">Car</option>
                </select>
                <input required placeholder="Hãng xe" value={pevForm.brand} onChange={(e) => setPevForm({ ...pevForm, brand: e.target.value })} className="border p-2 rounded-lg text-sm" />
                <input type="number" step="0.5" value={pevForm.battery_kwh} onChange={(e) => setPevForm({ ...pevForm, battery_kwh: Number(e.target.value) })} className="border p-2 rounded-lg text-sm" />
              </div>
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold">+ Đăng ký phương tiện</button>
            </form>

            <form onSubmit={handleReservePev} className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
              <h3 className="font-semibold text-slate-800">2. Đặt trước chỗ đỗ & Cổng sạc (Cọc 50,000₫)</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                <select required value={pevReserve.ev_id} onChange={(e) => setPevReserve({ ...pevReserve, ev_id: e.target.value })} className="border p-2 rounded-lg text-sm">
                  <option value="">-- Chọn xe cá nhân --</option>
                  {personalData.vehicles.map((ev: any) => <option key={ev.ev_id} value={ev.ev_id}>{ev.plate} ({ev.brand})</option>)}
                </select>
                <select value={pevReserve.hub_id} onChange={(e) => setPevReserve({ ...pevReserve, hub_id: e.target.value })} className="border p-2 rounded-lg text-sm">
                  {hubs.map((h) => <option key={h.hub_id} value={h.hub_id}>{h.name} ({h.available_slots} chỗ, {h.ports_available} sạc)</option>)}
                </select>
                <input type="number" min={5} max={95} value={pevReserve.current_soc} onChange={(e) => setPevReserve({ ...pevReserve, current_soc: Number(e.target.value) })} placeholder="Pin hiện tại (%)" className="border p-2 rounded-lg text-sm" />
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={pevReserve.request_charging} onChange={(e) => setPevReserve({ ...pevReserve, request_charging: e.target.checked })} />
                  Đăng ký sạc điện
                </label>
              </div>
              <button type="submit" disabled={!pevReserve.ev_id} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-semibold disabled:opacity-40">
                Đặt chỗ & Khóa cọc 50,000₫
              </button>
            </form>

            <div className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
              <h3 className="font-semibold text-slate-800">3. Quản lý đặt chỗ, Check-in & Check-out xe cá nhân</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 bg-slate-50 p-3 rounded-lg text-xs">
                <div>Giờ đỗ (mô phỏng): <input type="number" step="0.5" min={0.5} value={pevCheckout.duration_hours} onChange={(e) => setPevCheckout({ ...pevCheckout, duration_hours: Number(e.target.value) })} className="border p-1 rounded w-20 bg-white" /></div>
                <div>Điện sạc kWh: <input type="number" step="0.5" min={0} value={pevCheckout.kwh_charged} onChange={(e) => setPevCheckout({ ...pevCheckout, kwh_charged: Number(e.target.value) })} className="border p-1 rounded w-20 bg-white" /></div>
                <div>Quá hạn rút sạc (phút): <input type="number" step="5" min={0} value={pevCheckout.overstay_minutes} onChange={(e) => setPevCheckout({ ...pevCheckout, overstay_minutes: Number(e.target.value) })} className="border p-1 rounded w-20 bg-white" /></div>
              </div>
              <div className="space-y-2">
                {personalData.reservations.map((r: any) => (
                  <div key={r.reservation_id} className="p-3 border rounded-lg flex flex-wrap justify-between items-center text-xs gap-2">
                    <div>
                      <span className="font-mono font-bold">{r.reservation_id}</span> • Xe: <strong>{r.ev_id}</strong> • Hub: <strong>{r.hub_id}</strong> •
                      Sạc: <strong>{r.request_charging ? 'Có' : 'Không'}</strong> • Trạng thái: <strong className="text-blue-600">{r.status}</strong>
                    </div>
                    <div className="flex gap-2">
                      {r.status === 'RESERVED' && (
                        <button onClick={() => handleCheckinPev(r.reservation_id)} className="px-3 py-1.5 bg-emerald-600 text-white rounded font-semibold">
                          🚪 Check-in mở barie
                        </button>
                      )}
                      {r.status === 'CHECKED_IN' && (
                        <button onClick={() => handleCheckoutPev(r.reservation_id)} className="px-3 py-1.5 bg-blue-600 text-white rounded font-semibold">
                          🧾 Check-out & Quyết toán
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              {lastPevInvoice && (
                <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-xs">
                  Hóa đơn <strong>{lastPevInvoice.invoice_id}</strong>: Phí đỗ {lastPevInvoice.parking_fee.toLocaleString()}đ + Điện {lastPevInvoice.energy_fee.toLocaleString()}đ + Overstay {lastPevInvoice.overstay_fee.toLocaleString()}đ = <strong>{lastPevInvoice.total_amount.toLocaleString()}đ</strong>
                </div>
              )}
            </div>
          </div>
        )}

        {/* SUBSYSTEM 3 */}
        {activeTab === 'SS3' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {hubs.map((h) => (
                <div key={h.hub_id} className="bg-white p-5 rounded-xl shadow-sm border space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-bold text-slate-800 flex items-center gap-1.5">
                        <MapPin className="w-4 h-4 text-blue-600" /> {h.name}
                      </h4>
                      <p className="text-xs text-slate-400">{h.hub_id}</p>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                      h.alert_level === 'CRITICAL' || h.alert_level === 'FULL' ? 'bg-red-100 text-red-700' :
                      h.alert_level === 'WARNING' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'
                    }`}>
                      {h.occupancy_pct}% ({h.alert_level})
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-3 rounded-lg">
                    <div>Chỗ trống: <strong>{h.available_slots}/{h.total_slots}</strong></div>
                    <div>Cổng sạc: <strong>{h.ports_available}/{h.ports_total}</strong></div>
                    <div>Xe tại trạm: <strong>{h.current_vehicles?.length || 0}</strong></div>
                    <div>Giữ chỗ trước: <strong>{h.destination_holds}</strong></div>
                  </div>
                </div>
              ))}
            </div>

            {isOperator && forecast.length > 0 && (
              <div className="bg-white p-6 rounded-xl shadow-sm border">
                <h3 className="font-semibold text-slate-800 mb-3">📈 Dự báo nhu cầu 24 giờ tới</h3>
                <div className="grid grid-cols-4 md:grid-cols-8 gap-2 text-xs">
                  {forecast.slice(0, 16).map((f) => (
                    <div key={f.hour} className="p-2 border rounded bg-slate-50">
                      <div className="font-bold">{f.hour}</div>
                      <div>Đến: {f.arrivals} SV</div>
                      <div>Chờ: {f.queue_length} ({f.wait_time_min}p)</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* SUBSYSTEM 4 */}
        {activeTab === 'SS4' && (
          <div className="space-y-6">
            <form onSubmit={handleCreateDispatch} className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
              <h3 className="font-semibold text-slate-800">🚚 Tạo lệnh điều phối cân bằng tải (OPERATOR)</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs text-slate-500 mb-1">Hub nguồn</label>
                  <select value={dispForm.source_hub_id} onChange={(e) => setDispForm({ ...dispForm, source_hub_id: e.target.value, vehicle_ids: [] })} className="w-full border p-2 rounded-lg text-sm">
                    {hubs.map((h) => <option key={h.hub_id} value={h.hub_id}>{h.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-500 mb-1">Hub đích</label>
                  <select value={dispForm.destination_hub_id} onChange={(e) => setDispForm({ ...dispForm, destination_hub_id: e.target.value })} className="w-full border p-2 rounded-lg text-sm">
                    {hubs.map((h) => <option key={h.hub_id} value={h.hub_id}>{h.name} (Trống {h.available_slots})</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-500 mb-1">Lý do điều phối</label>
                  <input value={dispForm.reason} onChange={(e) => setDispForm({ ...dispForm, reason: e.target.value })} className="w-full border p-2 rounded-lg text-sm" />
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {dispVehicles.map((v: any) => {
                  const checked = dispForm.vehicle_ids.includes(v.vehicle_id);
                  return (
                    <label key={v.vehicle_id} className="px-3 py-1.5 border rounded-lg text-xs flex items-center gap-1.5 cursor-pointer bg-slate-50">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => setDispForm({
                          ...dispForm,
                          vehicle_ids: checked ? dispForm.vehicle_ids.filter((id) => id !== v.vehicle_id) : [...dispForm.vehicle_ids, v.vehicle_id]
                        })}
                      />
                      {v.vehicle_id} ({v.battery_soc}%)
                    </label>
                  );
                })}
              </div>
              <button type="submit" disabled={!isOperator || dispForm.vehicle_ids.length === 0} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold disabled:opacity-40">
                Khởi tạo điều phối ({dispForm.vehicle_ids.length} xe)
              </button>
            </form>

            <div className="bg-white p-6 rounded-xl shadow-sm border space-y-3">
              <h3 className="font-semibold text-slate-800">📦 Danh sách lệnh điều phối & Tiếp nhận tại Hub đích</h3>
              {dispatches.map((d: any) => (
                <div key={d.dispatch_id} className="p-3 border rounded-lg flex justify-between items-center text-xs">
                  <div>
                    <strong>{d.dispatch_id}</strong>: {d.source_hub_id} → {d.destination_hub_id} • Xe: <code>{(d.vehicle_ids || []).join(', ')}</code> • {d.reason}
                  </div>
                  {isOperator && (
                    <button onClick={() => handleReceiveDispatch(d.dispatch_id)} className="px-3 py-1.5 bg-emerald-600 text-white rounded font-semibold">
                      Xác nhận đã nhận xe
                    </button>
                  )}
                </div>
              ))}
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
              <h3 className="font-semibold text-slate-800">🚨 Cách ly / Khôi phục sự cố Phương tiện & Cổng sạc</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <select value={incForm.hub_id} onChange={(e) => setIncForm({ ...incForm, hub_id: e.target.value, vehicle_id: '' })} className="border p-2 rounded-lg text-sm">
                  {hubs.map((h) => <option key={h.hub_id} value={h.hub_id}>{h.name}</option>)}
                </select>
                <select value={incForm.target_type} onChange={(e) => setIncForm({ ...incForm, target_type: e.target.value })} className="border p-2 rounded-lg text-sm">
                  <option value="VEHICLE">Phương tiện (Xe điện)</option>
                  <option value="PORT">Cổng sạc tại Hub</option>
                </select>
                {incForm.target_type === 'VEHICLE' && (
                  <select value={incForm.vehicle_id} onChange={(e) => setIncForm({ ...incForm, vehicle_id: e.target.value })} className="border p-2 rounded-lg text-sm">
                    <option value="">-- Chọn xe tại Hub --</option>
                    {(incHubObj?.current_vehicles || []).map((v: any) => (
                      <option key={v.vehicle_id} value={v.vehicle_id}>{v.vehicle_id} ({v.status})</option>
                    ))}
                  </select>
                )}
              </div>
              <div className="flex gap-3">
                <button disabled={!isOperator} onClick={() => handleIncidentAction('isolate')} className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-semibold disabled:opacity-40">
                  Cách ly sự cố (INCIDENT / OFFLINE)
                </button>
                <button disabled={!isOperator} onClick={() => handleIncidentAction('recover')} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-semibold disabled:opacity-40">
                  Hoàn tất sửa chữa & Khôi phục
                </button>
              </div>
            </div>
          </div>
        )}

        {/* SUBSYSTEM 5 */}
        {activeTab === 'SS5' && (
          <div className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
            <div className="flex flex-wrap justify-between items-center gap-3">
              <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                <BatteryCharging className="w-5 h-5 text-amber-500" /> Hàng đợi ưu tiên sạc (Trần 150 kW/trạm)
              </h3>
              {isOperator && (
                <div className="flex gap-2 items-center">
                  <select value={allocHub} onChange={(e) => setAllocHub(e.target.value)} className="border px-3 py-1.5 rounded-lg text-xs">
                    {hubs.map((h) => <option key={h.hub_id} value={h.hub_id}>{h.name} ({h.ports_available} cổng trống)</option>)}
                  </select>
                  <button onClick={handleAllocateCharging} className="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-semibold">
                    ⚡ Phân bổ cổng sạc
                  </button>
                </div>
              )}
            </div>
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b text-slate-500">
                <tr>
                  <th className="p-2.5">Hạng</th>
                  <th className="p-2.5">Mã xe</th>
                  <th className="p-2.5">Hub</th>
                  <th className="p-2.5">Mức Pin (SoC)</th>
                  <th className="p-2.5">Trạng thái</th>
                  <th className="p-2.5">Điểm ưu tiên (Score)</th>
                  <th className="p-2.5">Thao tác</th>
                </tr>
              </thead>
              <tbody>
                {chargingQueue.map((item, idx) => (
                  <tr key={item.vehicle_id} className="border-b">
                    <td className="p-2.5 font-bold">#{idx + 1}</td>
                    <td className="p-2.5 font-mono">{item.vehicle_id}</td>
                    <td className="p-2.5">{item.hub_id}</td>
                    <td className="p-2.5">
                      <span className={`font-bold ${item.battery_soc < 20 ? 'text-red-600' : 'text-slate-700'}`}>{item.battery_soc}%</span>
                    </td>
                    <td className="p-2.5">{item.status}</td>
                    <td className="p-2.5 font-bold text-blue-600">{item.priority_score}</td>
                    <td className="p-2.5">
                      {isOperator && item.status === 'CHARGING' && (
                        <button onClick={() => handleUnplugCharging(item.vehicle_id)} className="px-2.5 py-1 bg-emerald-600 text-white rounded font-semibold">
                          Rút sạc
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* SUBSYSTEM 6 & 7 */}
        {activeTab === 'SS67' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
              <h3 className="font-semibold text-slate-800">🚇 SS6: Mô phỏng Metro Surge</h3>
              <select value={surgeForm.target_hub_id} onChange={(e) => setSurgeForm({ ...surgeForm, target_hub_id: e.target.value })} className="w-full border p-2 rounded-lg text-sm">
                {hubs.map((h) => <option key={h.hub_id} value={h.hub_id}>{h.name}</option>)}
              </select>
              <input type="number" min={1} max={100} value={surgeForm.num_new_students} onChange={(e) => setSurgeForm({ ...surgeForm, num_new_students: Number(e.target.value) })} className="w-full border p-2 rounded-lg text-sm" />
              <button
                disabled={!isOperator}
                onClick={async () => {
                  const res = await api.post('/api/hubs/simulate/metro-surge', surgeForm);
                  setSurgePreview(res.data);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold disabled:opacity-40"
              >
                Chạy Preview Metro Surge
              </button>
              {surgePreview && (
                <div className="p-3 bg-slate-50 rounded-lg text-xs space-y-1 border">
                  <div>Trạm: <strong>{surgePreview.hub_name}</strong></div>
                  <div>Tiếp nhận: <strong>{surgePreview.admitted_students}</strong> | Từ chối: <strong>{surgePreview.unserved_students}</strong></div>
                  <div>Chỗ trống: {surgePreview.before_slots} → <strong>{surgePreview.after_slots}</strong> ({surgePreview.final_occupancy_pct}% đầy)</div>
                </div>
              )}
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
              <h3 className="font-semibold text-slate-800">💥 SS7: Mô phỏng Port Failure</h3>
              <select value={failForm.target_hub_id} onChange={(e) => setFailForm({ ...failForm, target_hub_id: e.target.value })} className="w-full border p-2 rounded-lg text-sm">
                {hubs.map((h) => <option key={h.hub_id} value={h.hub_id}>{h.name}</option>)}
              </select>
              <input type="number" min={1} max={15} value={failForm.num_ports_down} onChange={(e) => setFailForm({ ...failForm, num_ports_down: Number(e.target.value) })} className="w-full border p-2 rounded-lg text-sm" />
              <button
                disabled={!isOperator}
                onClick={async () => {
                  const res = await api.post('/api/hubs/simulate/port-failure', failForm);
                  setFailPreview(res.data);
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-semibold disabled:opacity-40"
              >
                Chạy Preview Port Failure
              </button>
              {failPreview && (
                <div className="p-3 bg-slate-50 rounded-lg text-xs space-y-1 border">
                  <div>Cổng hỏng: <strong>{failPreview.failed_ports_total}</strong> | Phiên bị ngắt: <strong>{failPreview.busy_ports_interrupted}</strong></div>
                  <div>Xe gián đoạn: <strong>{failPreview.interrupted_vehicles.join(', ') || 'Không có'}</strong></div>
                  <div>Cổng còn lại: <strong>{failPreview.remaining_available_ports}</strong></div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};