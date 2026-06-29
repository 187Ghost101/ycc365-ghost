package com.ghost1o1.ycc365;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.graphics.Color;
import android.graphics.Typeface;
import android.view.Gravity;
import android.content.Intent;
import android.net.Uri;
import android.widget.Button;
import android.view.View;
import java.io.*;
import android.content.res.AssetManager;

public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // ─── ScrollView principal pour le contenu long ───
        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(Color.parseColor("#0a0f1e"));
        scroll.setPadding(24, 24, 24, 24);

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(8, 8, 8, 8);

        // ─── Banner Ghost1o1 ───
        TextView banner = new TextView(this);
        banner.setText("🏴‍☠️  YCC365 GHOST SCANNER  🏴‍☠️");
        banner.setTextSize(22);
        banner.setTextColor(Color.parseColor("#ffd60a"));
        banner.setTypeface(null, Typeface.BOLD);
        banner.setGravity(Gravity.CENTER);
        banner.setPadding(0, 16, 0, 8);

        // ─── Signature ───
        TextView signature = new TextView(this);
        signature.setText("Signé Ghost1o1 — IoT Pentest Toolkit");
        signature.setTextSize(12);
        signature.setTextColor(Color.parseColor("#4da6ff"));
        signature.setGravity(Gravity.CENTER);
        signature.setPadding(0, 0, 0, 24);

        // ─── Sous-titre ───
        TextView subtitle = new TextView(this);
        subtitle.setText("═══════════════════════════════\n" +
                        "AUDIT CAMÉRA YCC365 / IPCAM\n" +
                        "═══════════════════════════════");
        subtitle.setTextSize(14);
        subtitle.setTextColor(Color.parseColor("#94a3b8"));
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setPadding(0, 0, 0, 20);

        // ─── Section 1 : Modules ───
        TextView modulesTitle = new TextView(this);
        modulesTitle.setText("📦 MODULES INCLUS");
        modulesTitle.setTextSize(16);
        modulesTitle.setTextColor(Color.parseColor("#ffd60a"));
        modulesTitle.setTypeface(null, Typeface.BOLD);
        modulesTitle.setPadding(0, 12, 0, 8);

        TextView modules = new TextView(this);
        modules.setText(
            "✅ 16 ports YCC365 scannés\n" +
            "   (34567, 34599, 9527, 554, 8000,\n" +
            "    8899, 80, 443, 23, 8080…)\n\n" +
            "✅ 23 couples credentials testés\n" +
            "   admin/admin, admin/12345, root/xmhdipc…\n\n" +
            "✅ 21 URLs RTSP énumérées\n" +
            "   /onvif/streaming/channels/101\n" +
            "   /11, /12, /live/ch00_0…\n\n" +
            "✅ Détection backdoor Telnet Hipcam\n" +
            "✅ Scan ONVIF + dump device info\n" +
            "✅ Bruteforce HTTP Basic Auth\n" +
            "✅ Export rapport JSON"
        );
        modules.setTextSize(13);
        modules.setTextColor(Color.parseColor("#e8edf5"));
        modules.setPadding(8, 0, 8, 16);

        // ─── Section 2 : Instructions ───
        TextView usageTitle = new TextView(this);
        usageTitle.setText("🚀 UTILISATION");
        usageTitle.setTextSize(16);
        usageTitle.setTextColor(Color.parseColor("#ffd60a"));
        usageTitle.setTypeface(null, Typeface.BOLD);
        usageTitle.setPadding(0, 12, 0, 8);

        TextView usage = new TextView(this);
        usage.setText(
            "1. Installer Termux (F-Droid)\n" +
            "2. Lancer Termux\n" +
            "3. Exécuter la commande :\n\n" +
            "   bash /sdcard/ycc365-ghost.sh\n\n" +
            "OU copier le script scanner.sh\n" +
            "depuis cette APK vers :\n" +
            "  /data/data/com.termux/files/home/"
        );
        usage.setTextSize(13);
        usage.setTextColor(Color.parseColor("#4da6ff"));
        usage.setPadding(8, 0, 8, 16);

        // ─── Section 3 : Cibler une caméra ───
        TextView targetTitle = new TextView(this);
        targetTitle.setText("🎯 CIBLE TYPIQUE");
        targetTitle.setTextSize(16);
        targetTitle.setTextColor(Color.parseColor("#ffd60a"));
        targetTitle.setTypeface(null, Typeface.BOLD);
        targetTitle.setPadding(0, 12, 0, 8);

        TextView target = new TextView(this);
        target.setText(
            "Caméra YCC365 Plus (Temu/AliExpress)\n\n" +
            "• Trouver IP caméra :\n" +
            "  nmap -sn 192.168.1.0/24\n\n" +
            "• Lancer le scan :\n" +
            "  bash ycc365-ghost.sh\n" +
            "  → IP: 192.168.1.X\n\n" +
            "• Ports par défaut :\n" +
            "  HTTP  : 80, 34599, 8000\n" +
            "  RTSP  : 554 (souvent sans auth)\n" +
            "  Telnet: 9527 (backdoor xmhdipc)\n" +
            "  ONVIF : 8899"
        );
        target.setTextSize(13);
        target.setTextColor(Color.parseColor("#ff3860"));
        target.setPadding(8, 0, 8, 16);

        // ─── Section 4 : Disclaimer ───
        TextView disclaimerTitle = new TextView(this);
        disclaimerTitle.setText("⚠️  AVERTISSEMENT LÉGAL");
        disclaimerTitle.setTextSize(16);
        disclaimerTitle.setTextColor(Color.parseColor("#ffd60a"));
        disclaimerTitle.setTypeface(null, Typeface.BOLD);
        disclaimerTitle.setPadding(0, 12, 0, 8);

        TextView disclaimer = new TextView(this);
        disclaimer.setText(
            "Outil destiné EXCLUSIVEMENT à\n" +
            "l'audit de vos PROPRES équipements.\n\n" +
            "Toute utilisation sur des systèmes\n" +
            "tiers sans autorisation écrite\n" +
            "est ILLÉGALE (CFAA, Computer Misuse\n" +
            "Act, Art. 323-1 CP France).\n\n" +
            "Auteur : Ghost1o1\n" +
            "Usage : pentest autorisé uniquement"
        );
        disclaimer.setTextSize(12);
        disclaimer.setTextColor(Color.parseColor("#94a3b8"));
        disclaimer.setPadding(8, 0, 8, 16);

        // ─── Footer ───
        TextView footer = new TextView(this);
        footer.setText("\n═══════════════════════════════\n" +
                      "Ghost1o1 • Pentest • 2026\n" +
                      "═══════════════════════════════");
        footer.setTextSize(11);
        footer.setTextColor(Color.parseColor("#4da6ff"));
        footer.setGravity(Gravity.CENTER);
        footer.setPadding(0, 24, 0, 16);

        // ─── Assemble ───
        layout.addView(banner);
        layout.addView(signature);
        layout.addView(subtitle);
        layout.addView(modulesTitle);
        layout.addView(modules);
        layout.addView(usageTitle);
        layout.addView(usage);
        layout.addView(targetTitle);
        layout.addView(target);
        layout.addView(disclaimerTitle);
        layout.addView(disclaimer);
        layout.addView(footer);
        scroll.addView(layout);
        setContentView(scroll);
    }
}
