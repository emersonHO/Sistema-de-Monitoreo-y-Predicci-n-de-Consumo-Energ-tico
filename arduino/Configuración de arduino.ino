#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Configuración de pines
const int PIN_SENSOR = 2; // Sensor de proximidad
const int PIN_LIGHT = 3;  // Salida de luz

// Configuración de LCD
LiquidCrystal_I2C lcd(0x27, 16, 2); // Cambia 0x27 si tu LCD tiene otra dirección

// Potencia de la carga (en Watts)
const float POTENCIA_CARGA = 60.0;

// Variables de estado
bool luzEncendida = false;
unsigned long tiempoEncendido = 0;
unsigned long tiempoInicio = 0;
unsigned long tiempoApagado = 0;
bool esperandoApagar = false;

// Acumuladores
unsigned long tiempoTotalAcumulado = 0; // en segundos
float energiaTotalAcumulada = 0.0;
bool explicacionEnviada = false;

// Variables para evitar flicker en LCD
unsigned long ultimoTiempoMostrado = 0;
bool ultimoEstadoLuz = false;

// Función para limpiar una línea del LCD
void limpiarLineaLCD(uint8_t linea) {
  lcd.setCursor(0, linea);
  lcd.print("                "); // 16 espacios
}

// Función para formatear tiempo en hh:mm:ss
template<typename T>
void imprimirTiempo(T tiempoSegundos, Stream &out) {
  unsigned long h = tiempoSegundos / 3600;
  unsigned long m = (tiempoSegundos % 3600) / 60;
  unsigned long s = tiempoSegundos % 60;
  if (h < 10) { out.print('0'); }
  out.print(h); out.print(":");
  if (m < 10) { out.print('0'); }
  out.print(m); out.print(":");
  if (s < 10) { out.print('0'); }
  out.print(s);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_SENSOR, INPUT);
  pinMode(PIN_LIGHT, OUTPUT);
  digitalWrite(PIN_LIGHT, LOW);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Luz: APAGADA   ");
  limpiarLineaLCD(1);
  lcd.setCursor(0, 1);
  lcd.print("Tiempo: 00:00:00");
  ultimoEstadoLuz = false;
  ultimoTiempoMostrado = 0;
}

void loop() {
  int sensor = digitalRead(PIN_SENSOR);
  unsigned long ahora = millis();

  if (sensor == HIGH && !luzEncendida) {
    // Activación
    luzEncendida = true;
    esperandoApagar = false;
    tiempoInicio = ahora;
    digitalWrite(PIN_LIGHT, HIGH);
    Serial.println("Luz ACTIVADA");
    limpiarLineaLCD(0);
    lcd.setCursor(0, 0);
    lcd.print("Luz: ENCENDIDA ");
    limpiarLineaLCD(1);
    lcd.setCursor(0, 1);
    lcd.print("Tiempo: 00:00:00");
    ultimoTiempoMostrado = 0;
    ultimoEstadoLuz = true;
  }

  // Si el sensor se vuelve a activar durante la cuenta regresiva, cancelar el apagado y continuar el conteo
  if (sensor == HIGH && luzEncendida && esperandoApagar) {
    esperandoApagar = false;
  }

  // Si el sensor se apaga y la luz está encendida y no está esperando apagar, iniciar cuenta regresiva
  if (sensor == LOW && luzEncendida && !esperandoApagar) {
    esperandoApagar = true;
    tiempoApagado = ahora;
  }

  // Si está esperando apagar y se cumple el tiempo, apagar la luz y mostrar reporte
  if (esperandoApagar && (ahora - tiempoApagado >= 5000)) {
    luzEncendida = false;
    esperandoApagar = false;
    digitalWrite(PIN_LIGHT, LOW);
    unsigned long tiempoEvento = (ahora - tiempoInicio) / 1000; // en segundos
    float energiaEvento = (POTENCIA_CARGA * tiempoEvento) / 3600.0; // Wh
    tiempoTotalAcumulado += tiempoEvento;
    energiaTotalAcumulada += energiaEvento;
    if (!explicacionEnviada) {
      Serial.println("REPORTE: tiempo_evento (hh:mm:ss), energia_evento (Wh), tiempo_total (hh:mm:ss), energia_total (Wh)");
      Serial.println("Cada linea de reporte contiene los datos del ultimo evento y los acumulados.");
      Serial.println("Los datos estan separados por comas para facilitar su copia en Excel.");
      Serial.println("Formato: tiempo del evento, energia del evento, tiempo total, energia total.");
      explicacionEnviada = true;
    }
    Serial.print("REPORTE, ");
    imprimirTiempo(tiempoEvento, Serial); Serial.print(", ");
    Serial.print(energiaEvento, 3); Serial.print(", ");
    imprimirTiempo(tiempoTotalAcumulado, Serial); Serial.print(", ");
    Serial.println(energiaTotalAcumulada, 3);
    limpiarLineaLCD(0);
    lcd.setCursor(0, 0);
    lcd.print("Luz: APAGADA   ");
    limpiarLineaLCD(1);
    lcd.setCursor(0, 1);
    lcd.print("Tiempo: 00:00:00");
    ultimoEstadoLuz = false;
    ultimoTiempoMostrado = 0;
  }

  // Actualiza LCD si la luz esta encendida o esperando apagar
  if (luzEncendida || esperandoApagar) {
    unsigned long tiempoActual = (ahora - tiempoInicio) / 1000;
    if (!ultimoEstadoLuz) {
      limpiarLineaLCD(0);
      lcd.setCursor(0, 0);
      lcd.print("Luz: ENCENDIDA ");
      ultimoEstadoLuz = true;
    }
    if (tiempoActual != ultimoTiempoMostrado) {
      limpiarLineaLCD(1);
      lcd.setCursor(0, 1);
      lcd.print("Tiempo: ");
      unsigned long h = tiempoActual / 3600;
      unsigned long m = (tiempoActual % 3600) / 60;
      unsigned long s = tiempoActual % 60;
      if (h < 10) { lcd.print('0'); }
      lcd.print(h); lcd.print(":");
      if (m < 10) { lcd.print('0'); }
      lcd.print(m); lcd.print(":");
      if (s < 10) { lcd.print('0'); }
      lcd.print(s);
      lcd.print("   ");
      ultimoTiempoMostrado = tiempoActual;
    }
  } else {
    // Solo actualizar la línea del tiempo si el valor cambió, para evitar flicker
    if (!ultimoEstadoLuz) {
      lcd.setCursor(0, 0);
      lcd.print("Luz: APAGADA   ");
      ultimoEstadoLuz = false;
    }
    if (ultimoTiempoMostrado != tiempoTotalAcumulado) {
      lcd.setCursor(0, 1);
      lcd.print("Tiempo: ");
      unsigned long h = tiempoTotalAcumulado / 3600;
      unsigned long m = (tiempoTotalAcumulado % 3600) / 60;
      unsigned long s = tiempoTotalAcumulado % 60;
      if (h < 10) { lcd.print('0'); }
      lcd.print(h); lcd.print(":");
      if (m < 10) { lcd.print('0'); }
      lcd.print(m); lcd.print(":");
      if (s < 10) { lcd.print('0'); }
      lcd.print(s);
      lcd.print("   ");
      ultimoTiempoMostrado = tiempoTotalAcumulado;
    }
  }
  delay(100);
}
