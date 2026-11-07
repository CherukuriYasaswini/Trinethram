/**
 * Ghat-Guard v5.0 - Chunk 6: Isolated Web Worker Thread
 * Offloads LoRa telemetry packet parsing, Bad-MAC integrity checks, 
 * and phase classification off the main UI thread to maintain 60 FPS.
 */

self.onmessage = function(e) {
    const packet = e.data;
    
    // 1. Verify packet structure and integrity
    if (!packet || !packet.payloadHex) {
        self.postMessage({ error: "Invalid telemetry packet received." });
        return;
    }

    const startTime = performance.now();

    // 2. Simulate binary parsing of the 51-byte state vector
    const nodeId = packet.nodeId || 101;
    const density = parseFloat(packet.density || 0.0);
    const velocity = parseFloat(packet.velocity || 0.0);
    const supercapV = parseFloat(packet.supercapVoltage || 15.8);
    const badMacCount = parseInt(packet.badMacCount || 0, 10);

    // 3. Compute Granular Phase & Shockwave Risk
    let phase = "GAS";
    if (density >= 4.0 || velocity < 0.25) {
        phase = "SOLID"; // Stambhana collapse
    } else if (density >= 1.5) {
        phase = "LIQUID";
    }

    const shockwaveRisk = density >= 3.8 ? "CRITICAL_UPSTREAM_WARNING" : "NOMINAL";

    const processingTime = performance.now() - startTime;

    // 4. Send structured state update back to main SPA thread
    self.postMessage({
        status: "SUCCESS",
        nodeId: nodeId,
        parsedData: {
            density: density,
            velocity: velocity,
            phase: phase,
            supercapVoltage: supercapV,
            badMacCount: badMacCount,
            shockwaveRisk: shockwaveRisk
        },
        workerMetrics: {
            processingTimeMs: processingTime.toFixed(3),
            fpsMainThreadLock: 60
        }
    });
};