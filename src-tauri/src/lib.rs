use tauri::Manager;
use tauri::WebviewUrl;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! 最后的自由 Linux版已就绪。", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![greet])
        .setup(|app| {
            // Create window pointing to our local proxy server
            let url = WebviewUrl::External("http://127.0.0.1:18765".parse().unwrap());
            let _window = tauri::WebviewWindowBuilder::new(app, "main", url)
                .title("最后的自由 - Linux测试版")
                .inner_size(1366.0, 768.0)
                .resizable(true)
                .build()?;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
