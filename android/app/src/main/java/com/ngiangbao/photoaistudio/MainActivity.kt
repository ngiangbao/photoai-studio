package com.ngiangbao.photoaistudio

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.ngiangbao.photoaistudio.ui.PhotoAiStudioNavHost
import com.ngiangbao.photoaistudio.ui.theme.PhotoAIStudioTheme

/**
 * MainActivity.kt - Diem khoi chay ung dung, tuong duong main.py + MainWindow ben desktop.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            PhotoAIStudioTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    PhotoAiStudioNavHost()
                }
            }
        }
    }
}
