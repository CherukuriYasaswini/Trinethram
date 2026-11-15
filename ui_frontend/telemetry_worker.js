/**
 * Ghat-Guard v5.0 - Telemetry Worker (Offline-first UI)
 * Parses 51-byte LoRa mesh packets (hex) when provided and/or normalizes
 * telemetry fields off the main UI thread.
 *
 * 51-byte layout (little-endian): <IffBHH34s
 * nodeId(u32), density(f32), velocity(f32), phase(u8),
 * badMac(u16), supercapScaled(u16, V*100), padding(34)
 */

self.onmessage = function (e) {
  var input = e.data || {};
  var start = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();

  function toHexBytes(hex) {
    if (!hex || typeof hex !== 'string') return null;
    var clean = hex.replace(/[^0-9a-fA-F]/g, '');
    if (clean.length % 2 !== 0) return null;
    var out = new Uint8Array(clean.length / 2);
    for (var i = 0; i < clean.length; i += 2) {
      out[i / 2] = parseInt(clean.substr(i, 2), 16);
    }
    return out;
  }

  function parse51BytePacket(hex) {
    var bytes = toHexBytes(hex);
    if (!bytes || bytes.length !== 51) return null;
    var view = new DataView(bytes.buffer);
    var density = view.getFloat32(4, true);
    var velocity = view.getFloat32(8, true);
    var phaseCode = view.getUint8(12);
    var badMac = view.getUint16(13, true);
    var supercap = view.getUint16(15, true) / 100;
    var phase = phaseCode === 2 ? 'SOLID' : (phaseCode === 1 ? 'LIQUID' : 'GAS');
    if (!isFinite(density) || !isFinite(velocity) || !isFinite(supercap)) return null;
    return {
      nodeId: view.getUint32(0, true),
      density: density,
      velocity: velocity,
      phase: phase,
      phaseCode: phaseCode,
      badMacCount: badMac,
      supercapVoltage: supercap
    };
  }

  var parsedPacket = parse51BytePacket(input.payloadHex);
  if (!parsedPacket && !input.payloadHex && input.density == null) {
    self.postMessage({ error: 'Invalid telemetry packet received.' });
    return;
  }

  var density = parsedPacket ? parsedPacket.density : Number(input.density || 0);
  var velocity = parsedPacket ? parsedPacket.velocity : Number(input.velocity || 0);
  var supercapVoltage = parsedPacket ? parsedPacket.supercapVoltage : Number(input.supercapVoltage || 15.8);
  var badMacCount = parsedPacket ? parsedPacket.badMacCount : parseInt(input.badMacCount || 0, 10);
  var nodeId = parsedPacket ? parsedPacket.nodeId : (input.nodeId || 101);
  var phase = parsedPacket ? parsedPacket.phase : (density >= 4.0 || velocity < 0.25 ? 'SOLID' : (density >= 1.5 ? 'LIQUID' : 'GAS'));

  var shockwaveRisk = density >= 3.8 ? 'CRITICAL_UPSTREAM_WARNING' : 'NOMINAL';
  var end = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();

  self.postMessage({
    status: 'SUCCESS',
    nodeId: nodeId,
    parsedData: {
      density: density,
      velocity: velocity,
      phase: phase,
      supercapVoltage: supercapVoltage,
      badMacCount: badMacCount,
      breakBeforeMakeCount: Number(input.breakBeforeMakeCount || 0),
      waterLevel: input.waterLevel || '+2.14 m',
      shockwaveRisk: shockwaveRisk
    },
    workerMetrics: {
      processingTimeMs: Number(end - start).toFixed(3),
      parsed51BytePacket: !!parsedPacket
    }
  });
};
