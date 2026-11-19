import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Bike, BatteryCharging, MapPin, LogOut, Wallet, AlertTriangle, RefreshCw } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user, wallet, ledger, logout, refreshProfile } = useAuth();
  const [activeTab, setActiveTab] = useState<'SS1' | 'SS2' | 'SS3' | 'SS5'>('SS1');
  const [hubs, setHubs] = useState<any[]>([]);
  const [bookings, setBookings] = useState<any[]>([]);
  const [chargingQueue, setChargingQueue] = useState<any[]>([]);
  const [personalData, setPersonalData] = useState<any>({ vehicles: [], reservations: [] });

  // Form states SS1
  const [selectedHub, setSelectedHub] = useState('HUB-001');
  const [destHub, setDestHub] = useState('');
  const [selectedVehicle, setSelectedVehicle] = useState('');
  const [voucher, setVoucher] = useState('SVBK50');
  const [pinInput, setPinInput] = useState('');
  const [returnHub, setReturnHub] = useState('HUB-002');
  const [tripDuration, setTripDuration] = useState(25);

  // Form states SS2
  const [pevForm, setPevForm] = useState({ plate: '', type: 'scooter', brand: 'VinFast Klara S', battery_kwh: 3.5 });
  const [msg, setMsg] = useState<{ type: 'ok' | 'err'; text: string } | null>(null);

  const loadAllData = async () => {
    try {
      const [hubRes, bkRes, qRes, pevRes] = await Promise.all([
        api.get('/api/hubs'),
        api.get('/api/bookings/my'),
        api.get('/api/operations/charging-queue'),
        api.get('/api/personal-ev/my'),
      ]);
      setHubs(hubRes.data);
      setBookings(bkRes.data);
      setChargingQueue(qRes.data);
      setPersonalData(pevRes.data);
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
      loadAllData();
    } catch (e: any) {
      notify('err', e.response?.data?.detail || 'Lỗi trả xe');
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

  const activeBooking = bookings.find((b) => b.status === 'RESERVED' || b.status === 'IN_USE');
  const currentHubObj = hubs.find((h) => h.hub_id === selectedHub);
  const availVehicles = (currentHubObj?.current_vehicles || []).filter(
    (v: any) => v.status === 'AVAILABLE' && v.battery_soc >= 20
  );

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
              { id: 'SS5', label: '5. Lập lịch sạc thông minh' },
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
            {activeTab === 'SS5' && '⚡ Hàng đợi Lập lịch Sạc Thông minh (SS5)'}
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
                  Phương tiện: <strong>{activeBooking.vehicle_id}</strong> | Hub xuất phát: <strong>{activeBooking.hub_id}</strong> | Mã PIN: <strong className="text-blue-600">{activeBooking.pin_code}</strong>
                </p>

                {activeBooking.status === 'RESERVED' && (
                  <div className="flex gap-3 items-center pt-2">
                    <input
                      value={pinInput}
                      onChange={(e) => setPinInput(e.target.value)}
                      placeholder="Nhập PIN 4 số"
                      className="border px-3 py-2 rounded-lg text-sm w-40"
                    />
                    <button onClick={() => handlePickup(activeBooking.booking_id)} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-semibold">
                      🔓 Mở khóa & Nhận xe
                    </button>
                    <button onClick={() => handleCancel(activeBooking.booking_id)} className="px-4 py-2 bg-red-100 text-red-600 rounded-lg text-sm font-semibold">
                      Hủy đặt xe (Hoàn 100% cọc)
                    </button>
                  </div>
                )}

                {activeBooking.status === 'IN_USE' && (
                  <div className="flex flex-wrap gap-3 items-center pt-2">
                    <select value={returnHub} onChange={(e) => setReturnHub(e.target.value)} className="border px-3 py-2 rounded-lg text-sm">
                      {hubs.map((h) => (
                        <option key={h.hub_id} value={h.hub_id}>{h.name} (Trống {h.available_slots} chỗ)</option>
                      ))}
                    </select>
                    <input
                      type="number"
                      value={tripDuration}
                      onChange={(e) => setTripDuration(Number(e.target.value))}
                      className="border px-3 py-2 rounded-lg text-sm w-28"
                      min={1}
                    />
                    <span className="text-xs text-slate-500">phút di chuyển</span>
                    <button onClick={() => handleReturn(activeBooking.booking_id)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold">
                      ✅ Trả xe & Quyết toán
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
                <h3 className="font-semibold text-slate-800">Đặt giữ xe mới (Khóa cọc 50,000₫ • Miễn phí 30 phút đầu)</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs text-slate-500 mb-1">Hub xuất phát</label>
                    <select value={selectedHub} onChange={(e) => setSelectedHub(e.target.value)} className="w-full border p-2 rounded-lg text-sm">
                      {hubs.map((h) => (
                        <option key={h.hub_id} value={h.hub_id}>{h.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-slate-500 mb-1">Chọn xe (Pin ≥ 20%)</label>
                    <select value={selectedVehicle} onChange={(e) => setSelectedVehicle(e.target.value)} className="w-full border p-2 rounded-lg text-sm">
                      <option value="">-- Chọn phương tiện --</option>
                      {availVehicles.map((v: any) => (
                        <option key={v.vehicle_id} value={v.vehicle_id}>
                          {v.vehicle_id} ({v.type.toUpperCase()} - {v.battery_soc}% Pin)
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-slate-500 mb-1">Mã Voucher (SVBK50 / VNU2026)</label>
                    <input value={voucher} onChange={(e) => setVoucher(e.target.value)} className="w-full border p-2 rounded-lg text-sm" />
                  </div>
                </div>
                <button
                  disabled={!selectedVehicle}
                  onClick={handleBookVehicle}
                  className="px-5 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-semibold disabled:opacity-40"
                >
                  Xác nhận đặt giữ xe (50,000₫)
                </button>
              </div>
            )}

            {/* Sổ cái giao dịch */}
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
              <h3 className="font-semibold text-slate-800">Đăng ký xe điện cá nhân mới</h3>
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
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold">
                + Đăng ký phương tiện
              </button>
            </form>

            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <h3 className="font-semibold text-slate-800 mb-3">Danh sách xe cá nhân của bạn</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {personalData.vehicles.map((ev: any) => (
                  <div key={ev.ev_id} className="p-4 border rounded-lg flex justify-between items-center">
                    <div>
                      <div className="font-bold text-blue-600">{ev.plate}</div>
                      <div className="text-xs text-slate-500">{ev.brand} • Pin {ev.battery_kwh} kWh</div>
                    </div>
                    <span className="px-2.5 py-1 bg-emerald-100 text-emerald-700 rounded text-xs font-semibold">{ev.status}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* SUBSYSTEM 3 */}
        {activeTab === 'SS3' && (
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
                    h.alert_level === 'CRITICAL' ? 'bg-red-100 text-red-700' :
                    h.alert_level === 'WARNING' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'
                  }`}>
                    {h.occupancy_pct}% Lấp đầy
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
        )}

        {/* SUBSYSTEM 5 */}
        {activeTab === 'SS5' && (
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <h3 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
              <BatteryCharging className="w-5 h-5 text-amber-500" /> Hàng đợi ưu tiên sạc (Công suất trần 150 kW/trạm)
            </h3>
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b text-slate-500">
                <tr>
                  <th className="p-2.5">Hạng</th>
                  <th className="p-2.5">Mã xe</th>
                  <th className="p-2.5">Hub</th>
                  <th className="p-2.5">Mức Pin (SoC)</th>
                  <th className="p-2.5">Trạng thái</th>
                  <th className="p-2.5">Điểm ưu tiên (Score)</th>
                </tr>
              </thead>
              <tbody>
                {chargingQueue.map((item, idx) => (
                  <tr key={item.vehicle_id} className="border-b">
                    <td className="p-2.5 font-bold">#{idx + 1}</td>
                    <td className="p-2.5 font-mono">{item.vehicle_id}</td>
                    <td className="p-2.5">{item.hub_id}</td>
                    <td className="p-2.5">
                      <span className={`font-bold ${item.battery_soc < 20 ? 'text-red-600' : 'text-slate-700'}`}>
                        {item.battery_soc}%
                      </span>
                    </td>
                    <td className="p-2.5">{item.status}</td>
                    <td className="p-2.5 font-bold text-blue-600">{item.priority_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
};